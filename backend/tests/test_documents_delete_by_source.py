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
