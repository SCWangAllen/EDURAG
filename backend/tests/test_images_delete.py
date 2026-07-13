"""DELETE /api/images/{image_type}/{image_name} 端點測試

以獨立 FastAPI app 掛載真實 images router，並：
- monkeypatch router 模組內的 QUESTION_IMAGES_PATH / ANSWER_IMAGES_PATH 到 tmp 目錄
  （config 常數在 import 時即讀入，故必須 patch router 模組內引用的變數）
- 以 dependency_overrides 覆寫 get_db，回傳可控引用數的假 session
  （Mock 模式下真 get_db 會回 503，且 Depends 會在進入函式前就解析）
"""
import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.routers import images as images_module
from app.db.database import get_db


class _FakeResult:
    def __init__(self, items):
        self._items = items

    def scalars(self):
        return self

    def all(self):
        return self._items


class _FakeSession:
    """最小 AsyncSession 替身：execute 回固定引用清單。"""

    def __init__(self, references):
        self._references = references

    async def execute(self, stmt):
        return _FakeResult(self._references)

    async def commit(self):
        pass

    async def rollback(self):
        pass


@pytest.fixture
def image_dirs(tmp_path, monkeypatch):
    """建立 tmp 圖片目錄並改指 router 模組的路徑常數。"""
    q_dir = tmp_path / "questions"
    a_dir = tmp_path / "answers"
    q_dir.mkdir()
    a_dir.mkdir()
    monkeypatch.setattr(images_module, "QUESTION_IMAGES_PATH", q_dir)
    monkeypatch.setattr(images_module, "ANSWER_IMAGES_PATH", a_dir)
    return q_dir, a_dir


def _build_app(references):
    """掛真 images router 的獨立 app，並覆寫 get_db 回傳指定引用清單。"""
    app = FastAPI()
    app.include_router(images_module.router)

    async def _override_get_db():
        yield _FakeSession(references)

    app.dependency_overrides[get_db] = _override_get_db
    return app


async def _delete(app, path, **params):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.delete(path, params=params or None)


@pytest.mark.asyncio
async def test_delete_existing_image(image_dirs):
    """刪除存在且無引用的圖片 → 200，實體檔被移除。"""
    q_dir, _ = image_dirs
    img = q_dir / "sample.png"
    img.write_bytes(b"fake-image-bytes")

    app = _build_app(references=[])
    resp = await _delete(app, "/api/images/questions/sample")

    assert resp.status_code == 200
    data = resp.json()
    assert data["deleted"] == "sample"
    assert data["references_cleared"] == 0
    assert not img.exists()


@pytest.mark.asyncio
async def test_delete_missing_image_returns_404(image_dirs):
    """刪除不存在的圖片 → 404。"""
    app = _build_app(references=[])
    resp = await _delete(app, "/api/images/questions/does_not_exist")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_rejects_path_traversal(image_dirs):
    """image_name 含 .. → 400（路徑穿越防護）。"""
    app = _build_app(references=[])
    resp = await _delete(app, "/api/images/questions/evil..name")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_delete_with_references_without_force_returns_409(image_dirs):
    """有題目引用且未 force → 409，實體檔保留。"""
    q_dir, _ = image_dirs
    img = q_dir / "used.png"
    img.write_bytes(b"x")

    app = _build_app(references=[object(), object()])
    resp = await _delete(app, "/api/images/questions/used")

    assert resp.status_code == 409
    assert "2" in resp.json()["detail"]
    assert img.exists()  # 未被刪除


@pytest.mark.asyncio
async def test_force_delete_with_references(image_dirs):
    """有題目引用但帶 force=True → 200，實體檔被移除，回報原引用數。"""
    q_dir, _ = image_dirs
    img = q_dir / "used.png"
    img.write_bytes(b"x")

    app = _build_app(references=[object(), object()])
    resp = await _delete(app, "/api/images/questions/used", force=True)

    assert resp.status_code == 200
    data = resp.json()
    assert data["references_cleared"] == 2
    assert not img.exists()


@pytest.mark.asyncio
async def test_delete_answer_image(image_dirs):
    """answers 類型亦可刪除，走 ANSWER_IMAGES_PATH。"""
    _, a_dir = image_dirs
    img = a_dir / "ans.jpg"
    img.write_bytes(b"a")

    app = _build_app(references=[])
    resp = await _delete(app, "/api/images/answers/ans")

    assert resp.status_code == 200
    assert not img.exists()
