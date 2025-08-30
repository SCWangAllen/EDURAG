import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_templates_mock():
    """測試取得模板清單 (Mock 模式)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/templates/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "templates" in data
        assert "total" in data
        assert data["total"] > 0
        
        # 檢查是否有預設模板
        templates = data["templates"]
        subjects = {t["subject"] for t in templates}
        assert "健康" in subjects or "英文" in subjects or "歷史" in subjects

@pytest.mark.asyncio
async def test_get_subjects_mock():
    """測試取得科目清單 (Mock 模式)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/templates/subjects")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "subjects" in data
        assert isinstance(data["subjects"], list)
        assert len(data["subjects"]) > 0

@pytest.mark.asyncio
async def test_create_template_mock():
    """測試建立模板 (Mock 模式)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        template_data = {
            "subject": "健康",
            "name": "測試模板",
            "content": "這是一個測試模板的內容 {context}",
            "params": {"temperature": 0.8, "max_tokens": 300}
        }
        
        response = await client.post("/templates/", json=template_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["subject"] == "健康"
        assert data["name"] == "測試模板"
        assert "id" in data

@pytest.mark.asyncio
async def test_get_single_template_mock():
    """測試取得單一模板 (Mock 模式)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 先建立一個模板
        template_data = {
            "subject": "歷史",
            "name": "歷史測試模板",
            "content": "歷史題目模板 {context}"
        }
        create_response = await client.post("/templates/", json=template_data)
        created_template = create_response.json()
        
        # 取得這個模板
        template_id = created_template["id"]
        response = await client.get(f"/templates/{template_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == template_id
        assert data["subject"] == "歷史"

@pytest.mark.asyncio
async def test_template_not_found_mock():
    """測試模板不存在的情況 (Mock 模式)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/templates/999999")
        
        assert response.status_code == 404
        data = response.json()
        assert "模板不存在" in data["detail"]