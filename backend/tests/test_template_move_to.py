"""模板拖曳排序（POST /api/templates/{id}/move-to）的回歸測試。

分兩層，與 test_template_move.py 同結構：
1. plan_move_to() 是純函式（不觸 DB），直接單元測試移到頂/移到底/自身前後 no-op/未知 id。
2. HTTP 層透過 mock app 驗證 200/404/422 三種情境（不需 DB）。
"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.template_service import plan_move_to


# ---- plan_move_to 純函式 ---------------------------------------------------
def test_plan_move_to_top_via_before_first():
    ordered_ids = [1, 2, 3, 4]
    new_order = plan_move_to(ordered_ids, 4, before_id=1)
    assert new_order == [4, 1, 2, 3]


def test_plan_move_to_bottom_via_after_last():
    ordered_ids = [1, 2, 3, 4]
    new_order = plan_move_to(ordered_ids, 1, after_id=4)
    assert new_order == [2, 3, 4, 1]


def test_plan_move_to_before_self_is_noop():
    ordered_ids = [1, 2, 3]
    new_order = plan_move_to(ordered_ids, 2, before_id=2)
    assert new_order == [1, 2, 3]


def test_plan_move_to_after_self_is_noop():
    ordered_ids = [1, 2, 3]
    new_order = plan_move_to(ordered_ids, 2, after_id=2)
    assert new_order == [1, 2, 3]


def test_plan_move_to_middle_position():
    ordered_ids = [1, 2, 3, 4, 5]
    new_order = plan_move_to(ordered_ids, 5, after_id=2)
    assert new_order == [1, 2, 5, 3, 4]


def test_plan_move_to_unknown_template_id_raises():
    with pytest.raises(ValueError):
        plan_move_to([1, 2, 3], 999, before_id=1)


def test_plan_move_to_unknown_target_id_raises():
    with pytest.raises(ValueError):
        plan_move_to([1, 2, 3], 1, before_id=999)


def test_plan_move_to_requires_exactly_one_target():
    with pytest.raises(ValueError):
        plan_move_to([1, 2, 3], 1)
    with pytest.raises(ValueError):
        plan_move_to([1, 2, 3], 1, before_id=2, after_id=3)


# ---- HTTP 層（Mock 模式）---------------------------------------------------
@pytest.mark.asyncio
async def test_move_template_to_success_mock():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        list_resp = await client.get(
            "/api/templates/", params={"sort": "manual", "size": 100}
        )
        assert list_resp.status_code == 200
        templates = list_resp.json()["templates"]
        assert len(templates) >= 3
        ids = [t["id"] for t in templates]
        first_id, second_id, third_id = ids[0], ids[1], ids[2]

        # 把第三個拖到第一個之前
        resp = await client.post(
            f"/api/templates/{third_id}/move-to", json={"before_id": first_id}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["moved"] is True
        assert data["template_id"] == third_id
        assert data["order"][0] == third_id
        assert data["order"][1] == first_id
        assert data["order"][2] == second_id

        # 重新查詢清單，確認手動排序真的反映了移動結果
        after_resp = await client.get(
            "/api/templates/", params={"sort": "manual", "size": 100}
        )
        after_ids = [t["id"] for t in after_resp.json()["templates"]]
        assert after_ids[:3] == [third_id, first_id, second_id]


@pytest.mark.asyncio
async def test_move_template_to_self_is_noop_mock():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        list_resp = await client.get(
            "/api/templates/", params={"sort": "manual", "size": 100}
        )
        template_id = list_resp.json()["templates"][0]["id"]

        resp = await client.post(
            f"/api/templates/{template_id}/move-to", json={"before_id": template_id}
        )
        assert resp.status_code == 200
        assert resp.json()["moved"] is False


@pytest.mark.asyncio
async def test_move_template_to_missing_template_id_404_mock():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        list_resp = await client.get("/api/templates/", params={"size": 1})
        target_id = list_resp.json()["templates"][0]["id"]

        resp = await client.post(
            "/api/templates/999999/move-to", json={"before_id": target_id}
        )
        assert resp.status_code == 404
        assert "模板不存在" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_move_template_to_missing_target_id_404_mock():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        list_resp = await client.get("/api/templates/", params={"size": 1})
        template_id = list_resp.json()["templates"][0]["id"]

        resp = await client.post(
            f"/api/templates/{template_id}/move-to", json={"before_id": 999999}
        )
        assert resp.status_code == 404
        assert "模板不存在" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_move_template_to_requires_exactly_one_target_422_mock():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        list_resp = await client.get(
            "/api/templates/", params={"sort": "manual", "size": 100}
        )
        ids = [t["id"] for t in list_resp.json()["templates"]]

        # 都沒給
        resp_none = await client.post(f"/api/templates/{ids[0]}/move-to", json={})
        assert resp_none.status_code == 422

        # 兩個都給
        resp_both = await client.post(
            f"/api/templates/{ids[0]}/move-to",
            json={"before_id": ids[1], "after_id": ids[2]},
        )
        assert resp_both.status_code == 422
