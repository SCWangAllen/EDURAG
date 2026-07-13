from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import documents
from app.services.document_service import MockDocumentService

app = FastAPI()
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.dependency_overrides[documents.get_document_service] = lambda: MockDocumentService()

client = TestClient(app)


def test_size_over_100_is_allowed():
    """size 超過 100 不應被拒絕（修正前後端 le=100 會回 422）"""
    response = client.get("/api/documents/", params={"size": 500})
    assert response.status_code == 200


def test_omitted_size_returns_all_documents():
    """不帶 size 時回傳全部文件，不分頁"""
    response = client.get("/api/documents/")
    assert response.status_code == 200

    data = response.json()
    assert len(data["documents"]) == data["total"]
    assert data["page"] == 1
    assert data["pages"] == 1
    assert data["size"] == data["total"]


def test_explicit_size_still_paginates():
    """帶 size 時分頁行為維持不變"""
    response = client.get("/api/documents/", params={"page": 1, "size": 1})
    assert response.status_code == 200

    data = response.json()
    assert len(data["documents"]) == 1
    assert data["size"] == 1
    assert data["pages"] == data["total"]


def test_size_zero_is_rejected():
    """size=0 仍為不合法參數"""
    response = client.get("/api/documents/", params={"size": 0})
    assert response.status_code == 422
