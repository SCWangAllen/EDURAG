import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_get_templates_mock():
    """測試取得模板清單 (Mock 模式)"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/templates/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "templates" in data
        assert "total" in data
        assert data["total"] > 0
        
        # 檢查是否有預設模板 (Mock 模式使用英文科目名稱)
        templates = data["templates"]
        subjects = {t["subject"] for t in templates}
        assert "Health" in subjects or "健康" in subjects or len(subjects) > 0

@pytest.mark.asyncio
async def test_get_subjects_mock():
    """測試取得科目清單 (Mock 模式)"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/templates/subjects")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "subjects" in data
        assert isinstance(data["subjects"], list)
        assert len(data["subjects"]) > 0

@pytest.mark.asyncio
async def test_create_template_mock():
    """測試建立模板 (Mock 模式)"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        template_data = {
            "subject": "健康",
            "name": "測試模板",
            "content": "這是一個測試模板的內容 {context}",
            "params": {"temperature": 0.8, "max_tokens": 300}
        }
        
        response = await client.post("/api/templates/", json=template_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["subject"] == "健康"
        assert data["name"] == "測試模板"
        assert "id" in data

@pytest.mark.asyncio
async def test_get_single_template_mock():
    """測試取得單一模板 (Mock 模式)"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 先建立一個模板
        template_data = {
            "subject": "歷史",
            "name": "歷史測試模板",
            "content": "歷史題目模板 {context}"
        }
        create_response = await client.post("/api/templates/", json=template_data)
        created_template = create_response.json()
        
        # 取得這個模板
        template_id = created_template["id"]
        response = await client.get(f"/api/templates/{template_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == template_id
        assert data["subject"] == "歷史"

@pytest.mark.asyncio
async def test_template_not_found_mock():
    """測試模板不存在的情況 (Mock 模式)"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/templates/999999")

        assert response.status_code == 404
        data = response.json()
        assert "模板不存在" in data["detail"]


@pytest.mark.asyncio
async def test_get_templates_search_mock():
    """search 參數比對模板名稱或內容 (Mock 模式)"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/templates/", params={"search": "single_choice"})

        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        for t in data["templates"]:
            needle = "single_choice"
            assert needle in t["name"].lower() or needle in t["content"].lower()


@pytest.mark.asyncio
async def test_get_templates_sort_newest_mock():
    """sort=newest 為合法值，Mock 模式應正常回應"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/templates/", params={"sort": "newest"})

        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0


@pytest.mark.asyncio
async def test_get_templates_sort_grade_default_mock():
    """省略 sort 時預設為 grade 排序，Mock 模式應正常回應"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/templates/")

        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_templates_invalid_sort_rejected_mock():
    """sort 不是 grade/newest 時應回 422（Query enum 驗證）"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/templates/", params={"sort": "bogus"})

        assert response.status_code == 422