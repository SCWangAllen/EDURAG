import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app
import os

# 確保測試使用Mock模式
os.environ["USE_MOCK_API"] = "true"

client = TestClient(app)

def test_mock_ingest_schema():
    """測試Mock攝取API的Schema符合規範"""
    payload = {
        "subject": "chinese",
        "text": "這是一個測試文本。包含多個句子。用來測試攝取功能。",
        "title": "測試文件"
    }
    
    response = client.post("/api/ingest/", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    
    # 檢查回傳Schema
    assert "document_id" in data
    assert "chunks" in data
    assert "total_chunks" in data
    assert "processing_time" in data
    
    # 檢查chunks結構
    assert len(data["chunks"]) == data["total_chunks"]
    for chunk in data["chunks"]:
        assert "chunk_id" in chunk
        assert "text" in chunk
        assert "token_count" in chunk

def test_mock_generate_schema():
    """測試Mock生成API的Schema符合規範"""
    payload = {
        "subject": "chinese",
        "document_id": 999,
        "types": {
            "single_choice": 2,
            "cloze": 1,
            "short_answer": 1
        }
    }
    
    response = client.post("/api/generate/", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    
    # 檢查回傳Schema
    assert "items" in data
    assert "total_count" in data
    assert "generation_time" in data
    
    # 檢查題目總數
    expected_total = sum(payload["types"].values())
    assert data["total_count"] == expected_total
    assert len(data["items"]) == expected_total
    
    # 檢查題目結構
    for item in data["items"]:
        assert "type" in item
        assert "prompt" in item
        assert "answer" in item
        assert "explanation" in item
        assert "source" in item
        
        # 檢查來源結構
        source = item["source"]
        assert "document_id" in source
        assert "chunk_id" in source
        assert "chunk_text" in source

def test_generate_request_validation():
    """測試生成請求的驗證邏輯"""
    # 測試空的types字典
    payload = {
        "subject": "chinese",
        "document_id": 999,
        "types": {}
    }
    
    response = client.post("/api/generate/", json=payload)
    assert response.status_code == 422  # Validation error
    
    # 測試所有數量都是0
    payload = {
        "subject": "chinese", 
        "document_id": 999,
        "types": {
            "single_choice": 0,
            "cloze": 0
        }
    }
    
    response = client.post("/api/generate/", json=payload)
    assert response.status_code == 422  # Validation error