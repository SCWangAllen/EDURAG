"""GET /api/images/thumb/{type}/{filename}:產生並快取縮圖;找不到原圖 404。"""
import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from PIL import Image

from app.routers import images as images_module


@pytest.fixture
def dirs(tmp_path, monkeypatch):
    q = tmp_path / "questions"; a = tmp_path / "answers"; th = tmp_path / "thumbs"
    q.mkdir(); a.mkdir()
    monkeypatch.setattr(images_module, "QUESTION_IMAGES_PATH", q)
    monkeypatch.setattr(images_module, "ANSWER_IMAGES_PATH", a)
    monkeypatch.setattr(images_module, "THUMBS_PATH", th)
    return q, a, th


def _app():
    app = FastAPI()
    app.include_router(images_module.router)
    return app


async def _get(path):
    async with AsyncClient(transport=ASGITransport(app=_app()), base_url="http://test") as c:
        return await c.get(path)


@pytest.mark.asyncio
async def test_thumbnail_generated_cached_and_small(dirs):
    q, _, th = dirs
    Image.new("RGB", (1600, 900), (200, 30, 30)).save(q / "big.png")
    original_size = (q / "big.png").stat().st_size

    resp = await _get("/api/images/thumb/questions/big.png")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("image/jpeg")
    assert "max-age" in resp.headers.get("cache-control", "")
    thumb = th / "questions" / "big.jpg"
    assert thumb.exists()
    with Image.open(thumb) as im:
        assert max(im.size) <= images_module.THUMB_MAX_SIZE
    assert thumb.stat().st_size < original_size

    mtime = thumb.stat().st_mtime
    resp2 = await _get("/api/images/thumb/questions/big")  # 不含副檔名也可
    assert resp2.status_code == 200
    assert thumb.stat().st_mtime == mtime  # 第二次直接用快取


@pytest.mark.asyncio
async def test_transparent_png_gets_white_background(dirs):
    q, _, th = dirs
    Image.new("RGBA", (400, 400), (0, 0, 0, 0)).save(q / "clear.png")
    resp = await _get("/api/images/thumb/questions/clear.png")
    assert resp.status_code == 200
    with Image.open(th / "questions" / "clear.jpg") as im:
        assert im.mode == "RGB"
        assert im.getpixel((10, 10)) == (255, 255, 255)


@pytest.mark.asyncio
async def test_missing_source_is_404(dirs):
    resp = await _get("/api/images/thumb/answers/nope.jpg")
    assert resp.status_code == 404
