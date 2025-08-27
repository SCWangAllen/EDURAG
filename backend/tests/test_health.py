import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """測試健康檢查端點"""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "timestamp" in data
    assert "mode" in data
    assert "database_connected" in data
    assert "python_version" in data
    
    # 檢查基本值
    assert data["status"] in ["healthy", "degraded"]
    assert data["version"] == "1.0.0"
    assert isinstance(data["database_connected"], bool)