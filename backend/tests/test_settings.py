from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.mock_settings import router as settings_router
from app.core.llm_models import DEFAULT_MODEL

app = FastAPI()
app.include_router(settings_router)
client = TestClient(app)


def test_models_returns_curated_list():
    response = client.get("/api/settings/models")
    assert response.status_code == 200

    models = response.json()["models"]
    assert len(models) > 0
    ids = [m["id"] for m in models]
    assert DEFAULT_MODEL in ids
    # 每項都有 id + display_name
    for m in models:
        assert m["id"] and m["display_name"]


def test_get_model_returns_default():
    response = client.get("/api/settings/model")
    assert response.status_code == 200
    assert response.json()["model"] == DEFAULT_MODEL


def test_set_valid_model_then_get_reflects_it():
    put = client.put("/api/settings/model", json={"model": "claude-sonnet-5"})
    assert put.status_code == 200
    assert put.json()["model"] == "claude-sonnet-5"

    got = client.get("/api/settings/model")
    assert got.json()["model"] == "claude-sonnet-5"

    # 還原,避免影響其他測試
    client.put("/api/settings/model", json={"model": DEFAULT_MODEL})


def test_set_disallowed_model_rejected():
    response = client.put("/api/settings/model", json={"model": "gpt-4-turbo"})
    assert response.status_code == 400


def test_models_carry_group():
    models = client.get("/api/settings/models").json()["models"]
    assert all(m.get("group") in ("recommended", "other") for m in models)


def test_custom_claude_model_id_accepted_in_mock():
    """自訂輸入:mock 模式只檢查格式,claude-* 即可(真實模式會向 Anthropic 驗證)。"""
    put = client.put("/api/settings/model", json={"model": "claude-future-9"})
    assert put.status_code == 200
    assert client.get("/api/settings/model").json()["model"] == "claude-future-9"
    client.put("/api/settings/model", json={"model": DEFAULT_MODEL})


def test_custom_model_id_bad_format_rejected():
    for bad in ("Claude-Opus", "claude_opus", "claude-", "sonnet-5"):
        assert client.put("/api/settings/model", json={"model": bad}).status_code == 400, bad


def test_set_empty_model_rejected():
    response = client.put("/api/settings/model", json={"model": ""})
    # min_length=1 → 422 validation error
    assert response.status_code == 422
