"""文件頁碼（documents.page_number）區間解析 + 篩選的測試。

parse_page_range / page_range_conditions 是純函式，不觸 DB（page_range_conditions
用 literal_binds 編譯 SQL 檢查 WHERE 條件，做法沿用 test_documents_delete_by_source.py）。
路由測試沿用 test_documents_sort_and_sources.py 的作法：獨立組一個只掛 documents.router
的 app，用 dependency_overrides 換成 MockDocumentService，完全不碰真的 DB。
Excel 上傳解析測試沿用 test_image_blank_count.py 的作法：在記憶體中用 pandas 組一個
一列的 xlsx，直接丟進 parse_excel，不碰檔案系統。
"""
from io import BytesIO

import pandas as pd
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.page_range import page_range_conditions, parse_page_range
from app.db.models import Document
from app.routers import documents
from app.services.document_service import MockDocumentService
from app.services.upload_service import parse_excel

# ---- parse_page_range -----------------------------------------------------


def test_parse_page_range_none_and_blank_return_none():
    assert parse_page_range(None) is None
    assert parse_page_range("") is None
    assert parse_page_range("   ") is None


def test_parse_page_range_single_number():
    assert parse_page_range("71") == (71, 71)


def test_parse_page_range_simple_range():
    assert parse_page_range("100-101") == (100, 101)


def test_parse_page_range_reversed_range_is_swapped():
    assert parse_page_range("171-115") == (115, 171)


def test_parse_page_range_with_prefix():
    assert parse_page_range("pp. 115-171") == (115, 171)
    assert parse_page_range("p.12") == (12, 12)


def test_parse_page_range_excel_float_like_value_drops_decimal():
    # pandas 讀 Excel 數字格常把整數讀成 float（10.0、99.0）
    assert parse_page_range("10.0") == (10, 10)
    assert parse_page_range("99.0") == (99, 99)


def test_parse_page_range_fullwidth_digits_and_dash():
    assert parse_page_range("１０－１１") == (10, 11)


def test_parse_page_range_roman_numeral_is_unparseable():
    """序言常見的羅馬數字頁碼（例如 "xxii"）沒有阿拉伯數字，解析不出區間。"""
    assert parse_page_range("xxii") is None


# ---- page_range_conditions（編譯 SQL 檢查 WHERE 條件，不碰真的 DB） --------


def _sql(stmt) -> str:
    return str(stmt.compile(compile_kwargs={"literal_binds": True}))


def test_page_range_conditions_empty_when_no_bounds_given():
    assert page_range_conditions(Document.page_number) == []


def test_page_range_conditions_contains_regexp_replace_and_both_bounds():
    conditions = page_range_conditions(Document.page_number, page_from=115, page_to=171)
    sql = _sql(select(Document.id).where(*conditions))

    assert "regexp_replace" in sql
    assert "115" in sql
    assert "171" in sql
    # 全形數字先 translate 成半形;cast 成 NUMERIC(INTEGER 遇到 11 位以上數字串會溢位噴 500)
    assert "translate(" in sql
    assert "NUMERIC" in sql.upper()
    assert "INTEGER" not in sql.upper()


def test_page_range_conditions_only_from_or_only_to():
    from_only = _sql(
        select(Document.id).where(*page_range_conditions(Document.page_number, page_from=10))
    )
    assert "10" in from_only

    to_only = _sql(
        select(Document.id).where(*page_range_conditions(Document.page_number, page_to=20))
    )
    assert "20" in to_only


# ---- GET /api/documents/?page_from=&page_to= -------------------------------

app = FastAPI()
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.dependency_overrides[documents.get_document_service] = lambda: MockDocumentService()

client = TestClient(app)


def test_page_range_query_params_are_accepted():
    response = client.get("/api/documents/", params={"page_from": 10, "page_to": 20})
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data


def test_page_from_zero_is_rejected_with_422():
    response = client.get("/api/documents/", params={"page_from": 0})
    assert response.status_code == 422


def test_page_to_zero_is_rejected_with_422():
    response = client.get("/api/documents/", params={"page_to": 0})
    assert response.status_code == 422


# ---- Excel 上傳解析：page_unparseable 警示 ----------------------------------


def _build_xlsx(rows: list[dict]) -> bytes:
    df = pd.DataFrame(rows)
    buf = BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    return buf.getvalue()


def _row(page):
    return {
        "Words": "content",
        "Chapter": "Chapter 1",
        "Subject": "Health",
        "Imagesrelated": None,
        "Page": page,
    }


def test_upload_row_with_roman_numeral_page_gets_page_unparseable_warning():
    contents = _build_xlsx([_row("xxii")])
    docs = parse_excel(contents, "test.xlsx")

    assert docs[0]["page_number"] == "xxii"
    assert "page_unparseable" in docs[0]["warnings"]


def test_upload_row_with_valid_range_has_no_page_unparseable_warning():
    contents = _build_xlsx([_row("70-71")])
    docs = parse_excel(contents, "test.xlsx")

    assert docs[0]["page_number"] == "70-71"
    assert "page_unparseable" not in docs[0]["warnings"]


def test_upload_row_without_page_column_has_no_page_unparseable_warning():
    rows = [_row("70-71")]
    del rows[0]["Page"]
    contents = _build_xlsx(rows)
    docs = parse_excel(contents, "test.xlsx")

    assert docs[0]["page_number"] is None
    assert "page_unparseable" not in docs[0]["warnings"]


def test_page_filter_rejects_absurdly_large_values():
    """輸入框亂按出的超大數字在路由就擋下(422),不會進到 SQL"""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from app.routers import documents
    from app.services.document_service import MockDocumentService

    app = FastAPI()
    app.include_router(documents.router, prefix="/api/documents")
    app.dependency_overrides[documents.get_document_service] = lambda: MockDocumentService()
    client = TestClient(app)
    assert client.get("/api/documents/", params={"page_from": 99999999999}).status_code == 422
    assert client.get("/api/documents/", params={"page_to": 2000000}).status_code == 422
    assert client.get("/api/documents/", params={"page_from": 1, "page_to": 1000000}).status_code == 200
