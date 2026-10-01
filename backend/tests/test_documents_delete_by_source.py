"""POST /api/documents/delete-by-source 與 GET /api/documents/sources 的 subject/grade 篩選。

沿用 test_documents_sort_and_sources.py 的作法：獨立組一個只掛 documents.router 的 app，
用 dependency_overrides 換成 MockDocumentService，完全不碰真的 DB。
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import documents
from app.services.document_service import MockDocumentService

app = FastAPI()
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.dependency_overrides[documents.get_document_service] = lambda: MockDocumentService()

client = TestClient(app)


def test_delete_by_source_returns_expected_keys():
    response = client.post(
        "/api/documents/delete-by-source", json={"source_filename": "x.xlsx"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["success_count"] == 0
    assert data["failed_count"] == 0
    assert data["failed"] == []
    assert data["source_filename"] == "x.xlsx"


def test_delete_by_source_empty_filename_is_rejected_with_422():
    response = client.post(
        "/api/documents/delete-by-source", json={"source_filename": ""}
    )
    assert response.status_code == 422


def test_delete_by_source_missing_body_is_rejected_with_422():
    response = client.post("/api/documents/delete-by-source", json={})
    assert response.status_code == 422


def test_sources_with_subject_and_grade_filters_returns_200():
    response = client.get(
        "/api/documents/sources", params={"subject": "health", "grade": "G4"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert isinstance(data["sources"], list)


def test_delete_by_source_accepts_subject_and_grade_scope():
    """帶 subject / grade 限縮(與列表篩選一致)也要能通過驗證"""
    response = client.post(
        "/api/documents/delete-by-source",
        json={"source_filename": "x.xlsx", "subject": "Health", "grade": "G4"},
    )
    assert response.status_code == 200
    assert response.json()["source_filename"] == "x.xlsx"


# ---- 真正驗證 WHERE 條件(mock 模式下路由不會碰到 service,所以直接編譯 SQL 檢查)
from sqlalchemy import and_, select  # noqa: E402

from app.db.models import Document  # noqa: E402
from app.services.document_service import (  # noqa: E402
    source_scope_conditions,
    sources_query,
)


def _sql(stmt) -> str:
    return str(stmt.compile(compile_kwargs={"literal_binds": True}))


def test_sources_query_without_filters_only_excludes_null_filenames():
    sql = _sql(sources_query())
    assert "documents.source_filename IS NOT NULL" in sql
    assert "documents.subject" not in sql
    assert "documents.grade" not in sql


def test_sources_query_applies_subject_and_grade_filters():
    sql = _sql(sources_query(subject="Health", grade="G4"))
    assert "documents.subject = 'Health'" in sql
    assert "documents.grade = 'G4'" in sql


def test_delete_scope_matches_filename_and_optional_subject_grade():
    """刪整批時:畫面篩了科目/年級,就只刪該範圍;沒篩就整個檔名都刪"""
    whole = _sql(select(Document.id).where(and_(*source_scope_conditions("x.xlsx"))))
    assert "documents.source_filename = 'x.xlsx'" in whole
    assert "documents.grade" not in whole

    scoped = _sql(
        select(Document.id).where(
            and_(*source_scope_conditions("x.xlsx", subject="Health", grade="G4"))
        )
    )
    assert "documents.source_filename = 'x.xlsx'" in scoped
    assert "documents.subject = 'Health'" in scoped
    assert "documents.grade = 'G4'" in scoped
