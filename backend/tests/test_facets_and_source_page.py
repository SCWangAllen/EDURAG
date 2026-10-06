"""文件/問題 facets（faceted search）+ 問題 source_page（來源文件課本頁碼）的測試。

路由測試沿用 test_documents_sort_and_sources.py 的作法：獨立組一個只掛對應 router
的 app，用 dependency_overrides 換成 Mock*Service，完全不碰真的 DB。
facet_conditions / question_facet_conditions 是純函式，不觸 DB（沿用
test_page_range.py 的 literal_binds 編譯 SQL 做法）。
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import and_, select

from app.db.models import Document, Question
from app.routers import documents, questions
from app.services.document_service import (
    MockDocumentService,
    documents_list_query,
    facet_conditions,
    merge_all_grade_counts,
)
from app.services.question_service import MockQuestionService, _metadata_field, question_facet_conditions
from app.core.page_range import page_range_conditions


def _sql(stmt) -> str:
    return str(stmt.compile(compile_kwargs={"literal_binds": True}))


# ---- GET /api/documents/facets --------------------------------------------

documents_app = FastAPI()
documents_app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
documents_app.dependency_overrides[documents.get_document_service] = lambda: MockDocumentService()
documents_client = TestClient(documents_app)


def test_document_facets_returns_expected_keys():
    response = documents_client.get("/api/documents/facets")
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"subjects", "grades", "chapters"}
    assert isinstance(data["subjects"], list)
    # Mock 樣本資料全部是 health / G1~G6，應至少看得到一個 subject 選項
    assert any(item["value"] == "health" for item in data["subjects"])
    for item in data["subjects"]:
        assert set(item.keys()) == {"value", "count"}


def test_document_facets_with_filters_does_not_error():
    response = documents_client.get(
        "/api/documents/facets",
        params={"subject": "health", "grade": "G1", "chapter": "Chapter 1"},
    )
    assert response.status_code == 200


# ---- GET /api/documents/?fields= & ?ids= ----------------------------------


def test_documents_fields_light_omits_content():
    response = documents_client.get("/api/documents/", params={"fields": "light", "size": 1})
    assert response.status_code == 200
    doc = response.json()["documents"][0]
    assert "content" not in doc
    assert "image_data" not in doc


def test_documents_fields_full_is_default_and_keeps_content():
    response = documents_client.get("/api/documents/", params={"size": 1})
    assert response.status_code == 200
    doc = response.json()["documents"][0]
    assert "content" in doc


def test_documents_fields_bogus_is_rejected_with_422():
    response = documents_client.get("/api/documents/", params={"fields": "bogus"})
    assert response.status_code == 422


def test_documents_ids_returns_exactly_those_documents():
    response = documents_client.get("/api/documents/", params={"ids": "1,2"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert {doc["id"] for doc in data["documents"]} == {1, 2}
    # ids 路徑回完整內容
    assert all("content" in doc for doc in data["documents"])


def test_documents_ids_non_integer_is_rejected_with_422():
    response = documents_client.get("/api/documents/", params={"ids": "abc"})
    assert response.status_code == 422


def test_documents_ids_over_200_is_rejected_with_422():
    ids = ",".join(str(i) for i in range(1, 202))
    response = documents_client.get("/api/documents/", params={"ids": ids})
    assert response.status_code == 422


# ---- GET /api/questions/facets + source_page / page_from / page_to --------

questions_app = FastAPI()
questions_app.include_router(questions.router, prefix="/api/questions", tags=["questions"])
questions_app.dependency_overrides[questions.get_question_service] = lambda: MockQuestionService()
questions_client = TestClient(questions_app)


def test_question_facets_returns_expected_keys():
    response = questions_client.get("/api/questions/facets")
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"subjects", "grades", "question_types", "chapters", "difficulties"}


def test_question_facets_with_filters_does_not_error():
    response = questions_client.get(
        "/api/questions/facets",
        params={"subject": "Health", "question_type": "single_choice"},
    )
    assert response.status_code == 200


def test_questions_list_includes_source_page_field():
    response = questions_client.get("/api/questions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["questions"]) > 0
    assert "source_page" in data["questions"][0]


def test_questions_page_from_zero_is_rejected_with_422():
    response = questions_client.get("/api/questions/", params={"page_from": 0})
    assert response.status_code == 422


def test_questions_page_to_zero_is_rejected_with_422():
    response = questions_client.get("/api/questions/", params={"page_to": 0})
    assert response.status_code == 422


def test_questions_chapter_filter_param_is_accepted():
    response = questions_client.get("/api/questions/", params={"chapter": "Chapter 1"})
    assert response.status_code == 200


def test_questions_page_range_params_are_accepted():
    response = questions_client.get("/api/questions/", params={"page_from": 10, "page_to": 20})
    assert response.status_code == 200


# ---- compile-tests：questions 的 join + page filter SQL 組裝 ---------------


def test_questions_page_filter_statement_contains_outer_join_and_regexp_replace():
    """get_questions 用 page_from/page_to 篩選時套用的 join + 條件（沿用與 get_questions
    相同的組裝方式：outerjoin documents + page_range_conditions），編譯出的 SQL
    應包含 LEFT OUTER JOIN documents 與 regexp_replace（page_range_conditions 的實作細節）。
    """
    conditions = page_range_conditions(Document.page_number, page_from=10, page_to=20)
    stmt = (
        select(Question, Document.page_number)
        .outerjoin(Document, Question.document_id == Document.id)
        .where(and_(*conditions))
    )
    sql = _sql(stmt)
    assert "LEFT OUTER JOIN documents" in sql
    assert "regexp_replace" in sql


def test_questions_count_statement_applies_same_join_and_conditions():
    conditions = page_range_conditions(Document.page_number, page_from=10, page_to=20)
    from sqlalchemy import func

    stmt = (
        select(func.count(Question.id))
        .outerjoin(Document, Question.document_id == Document.id)
        .where(and_(*conditions))
    )
    sql = _sql(stmt)
    assert "LEFT OUTER JOIN documents" in sql
    assert "regexp_replace" in sql


# ---- compile-tests：facet_conditions 排除自身維度 ---------------------------


def test_document_facet_conditions_grade_excludes_grade_but_keeps_subject():
    conditions = facet_conditions("grade", subject="health", grade="G1")
    sql = _sql(select(Document.id).where(and_(*conditions)))

    assert "health" in sql
    assert "G1" not in sql
    assert "documents.grade" not in sql


def test_document_facet_conditions_subject_excludes_subject_but_keeps_grade():
    conditions = facet_conditions("subject", subject="health", grade="G1")
    sql = _sql(select(Document.id).where(and_(*conditions)))

    assert "G1" in sql
    assert "'health'" not in sql


def test_question_facet_conditions_grade_excludes_grade_but_keeps_subject():
    conditions = question_facet_conditions("grade", subject="Health", grade="G1")
    sql = _sql(select(Question.id).where(and_(*conditions)))

    assert "Health" in sql
    assert "G1" not in sql


def test_question_facet_conditions_page_range_filters_on_document_page_number():
    conditions = question_facet_conditions("grade", page_from=32, page_to=37)
    sql = _sql(select(Question.id).outerjoin(Document, Question.document_id == Document.id).where(and_(*conditions)))

    assert "documents.page_number" in sql
    assert "regexp_replace" in sql


def test_question_facet_conditions_without_page_range_has_no_page_condition():
    conditions = question_facet_conditions("grade", subject="Health")
    sql = _sql(select(Question.id).where(and_(*conditions)))

    assert "page_number" not in sql


def test_question_facets_accepts_page_range_params():
    response = questions_client.get("/api/questions/facets", params={"page_from": 32, "page_to": 37})
    assert response.status_code == 200
    assert set(response.json().keys()) == {"subjects", "grades", "question_types", "chapters", "difficulties"}


def test_question_facets_page_from_zero_is_rejected_with_422():
    response = questions_client.get("/api/questions/facets", params={"page_from": 0})
    assert response.status_code == 422


# ---- 年級 facet 的 'ALL' 併入各年級計數 ---------------------------------------

def test_merge_all_grade_counts_adds_all_rows_to_every_grade():
    items = [{"value": "G1", "count": 3}, {"value": "G2", "count": 5}, {"value": "ALL", "count": 2}]
    merged = merge_all_grade_counts(items)

    assert merged == [{"value": "G1", "count": 5}, {"value": "G2", "count": 7}, {"value": "ALL", "count": 2}]
    assert items[0]["count"] == 3  # 不改原 list


def test_merge_all_grade_counts_without_all_is_unchanged():
    items = [{"value": "G1", "count": 3}]
    assert merge_all_grade_counts(items) == items


# ---- fields=light 在 SQL 層省略大欄位 -----------------------------------------

def test_documents_list_query_light_defers_content_and_image_data():
    light = _sql(documents_list_query("light"))
    full = _sql(documents_list_query("full"))

    assert "documents.content" not in light
    assert "documents.image_data" not in light
    assert "documents.page_number" in light
    assert "documents.content" in full


# ---- _metadata_field 只接受白名單 key ------------------------------------------

def test_metadata_field_accepts_known_keys():
    for name in ("subject", "grade", "chapter", "difficulty"):
        assert "source_metadata" in _sql(select(_metadata_field(name)))


def test_metadata_field_rejects_unknown_key():
    import pytest

    with pytest.raises(ValueError):
        _metadata_field("x' OR '1'='1")
