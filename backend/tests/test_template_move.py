"""模板手動排序（sort=manual + POST /api/templates/{id}/move）的回歸測試。

分兩層：
1. plan_move() 是純函式（不觸 DB），直接單元測試上移/下移/邊界/凍結邏輯。
2. HTTP 層透過 mock app 驗證 up/down/edge 三種情境（不需 DB）。
"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.template_service import plan_move


# ---- plan_move 純函式 ------------------------------------------------------
def test_plan_move_freezes_null_sort_order_then_moves_up():
    # 三筆都還沒手動排序過（sort_order 全 None），目前顯示順序是 1, 2, 3
    ordered = [(1, None), (2, None), (3, None)]
    updates, moved, final = plan_move(ordered, 2, "up")

    assert moved is True
    # 凍結成 0, 10, 20，再把 id=2（10）與 id=1（0）互換
    assert dict(updates) == {1: 10, 2: 0, 3: 20}
    assert final == 0


def test_plan_move_down_swaps_with_next_when_already_frozen():
    ordered = [(1, 0), (2, 10), (3, 20)]
    updates, moved, final = plan_move(ordered, 1, "down")

    assert moved is True
    assert dict(updates) == {1: 10, 2: 0}
    assert final == 10


def test_plan_move_up_at_top_writes_nothing_even_when_unfrozen():
    updates, moved, final = plan_move([(1, None), (2, None), (3, None)], 1, "up")
    assert moved is False
    assert updates == []
    assert final == 0


def test_plan_move_down_at_bottom_is_noop():
    ordered = [(1, 0), (2, 10)]
    updates, moved, final = plan_move(ordered, 2, "down")

    assert moved is False
    assert updates == []
    assert final == 10


def test_plan_move_unknown_template_id_raises():
    with pytest.raises(ValueError):
        plan_move([(1, 0), (2, 10)], 999, "up")


# ---- HTTP 層（Mock 模式）---------------------------------------------------
@pytest.mark.asyncio
async def test_move_template_up_down_edge_mock():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # sort=manual 先確認合法值可用
        list_resp = await client.get(
            "/api/templates/", params={"sort": "manual", "size": 100}
        )
        assert list_resp.status_code == 200
        templates = list_resp.json()["templates"]
        assert len(templates) >= 2
        first_id, second_id = templates[0]["id"], templates[1]["id"]

        # 第二個往上移一格 → 應該變成 moved=true 且與第一個互換
        up_resp = await client.post(
            f"/api/templates/{second_id}/move", json={"direction": "up"}
        )
        assert up_resp.status_code == 200
        up_data = up_resp.json()
        assert up_data["moved"] is True
        assert up_data["template_id"] == second_id
        assert up_data["sort_order"] is not None

        # 換完之後重新排序，second_id 應該排到第一位
        after_resp = await client.get(
            "/api/templates/", params={"sort": "manual", "size": 100}
        )
        after_ids = [t["id"] for t in after_resp.json()["templates"]]
        assert after_ids[0] == second_id
        assert after_ids[1] == first_id

        # 現在 second_id 已經在最上面，再上移一次應該是邊界 no-op
        edge_resp = await client.post(
            f"/api/templates/{second_id}/move", json={"direction": "up"}
        )
        assert edge_resp.status_code == 200
        assert edge_resp.json()["moved"] is False

        # 下移一格換回來
        down_resp = await client.post(
            f"/api/templates/{second_id}/move", json={"direction": "down"}
        )
        assert down_resp.status_code == 200
        assert down_resp.json()["moved"] is True


@pytest.mark.asyncio
async def test_move_template_not_found_mock():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/templates/999999/move", json={"direction": "up"})
        assert resp.status_code == 404
        assert "模板不存在" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_move_template_invalid_direction_rejected_mock():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        list_resp = await client.get("/api/templates/", params={"size": 1})
        template_id = list_resp.json()["templates"][0]["id"]

        resp = await client.post(
            f"/api/templates/{template_id}/move", json={"direction": "sideways"}
        )
        assert resp.status_code == 422
