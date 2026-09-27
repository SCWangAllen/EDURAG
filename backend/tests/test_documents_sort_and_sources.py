"""GET /api/documents/ 的 sort/source_file 參數與新的 GET /api/documents/sources 端點。

沿用 test_documents_list_size.py 的作法：獨立組一個只掛 documents.router 的 app，
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


def test_sort_chapter_is_accepted():
    """chapter 是預設值，也應可顯式帶入"""
    response = client.get("/api/documents/", params={"sort": "chapter"})
    assert response.status_code == 200


def test_sort_newest_is_accepted():
    response = client.get("/api/documents/", params={"sort": "newest"})
    assert response.status_code == 200


def test_sort_omitted_defaults_without_error():
    response = client.get("/api/documents/")
    assert response.status_code == 200


def test_invalid_sort_value_is_rejected_with_422():
    response = client.get("/api/documents/", params={"sort": "bogus"})
    assert response.status_code == 422


def test_source_file_filter_does_not_error():
    """Mock 資料沒有 source_filename，篩選應回空清單而非出錯"""
    response = client.get("/api/documents/", params={"source_file": "some_upload.xlsx"})
    assert response.status_code == 200
    data = response.json()
    assert data["documents"] == []
    assert data["total"] == 0


def test_sources_endpoint_registered_before_document_id_route():
    """/sources 必須在 GET /{document_id} 動態路由之前被註冊，否則會被誤判成 document_id='sources'"""
    response = client.get("/api/documents/sources")
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert isinstance(data["sources"], list)
