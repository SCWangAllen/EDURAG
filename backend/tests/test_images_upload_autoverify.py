"""POST /api/images/upload/{image_type} 上傳後自動驗證引用題目。

沿用 test_images_delete 的做法:真 router、monkeypatch 圖片目錄到 tmp、覆寫 get_db 為假 session。
"""
import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.routers import images as images_module
from app.db.database import get_db


class _FakeQuestion:
    def __init__(self, question_image, answer_image=None):
        self.id = 1
        self.question_image = question_image
        self.answer_image = answer_image
        self.images_verified = False


class _FakeResult:
    def __init__(self, items):
        self._items = items

    def scalars(self):
        return self

    def all(self):
        return self._items


class _FakeSession:
    def __init__(self, questions):
        self.questions = questions
        self.committed = False

    async def execute(self, stmt):
        return _FakeResult(self.questions)

    async def commit(self):
        self.committed = True

    async def rollback(self):
        pass


@pytest.fixture
def image_dirs(tmp_path, monkeypatch):
    q_dir = tmp_path / "questions"
    a_dir = tmp_path / "answers"
    q_dir.mkdir()
    a_dir.mkdir()
    monkeypatch.setattr(images_module, "QUESTION_IMAGES_PATH", q_dir)
    monkeypatch.setattr(images_module, "ANSWER_IMAGES_PATH", a_dir)
    return q_dir, a_dir


def _build_app(session):
    app = FastAPI()
    app.include_router(images_module.router)

    async def _override_get_db():
        yield session

    app.dependency_overrides[get_db] = _override_get_db
    return app


async def _upload(app, image_type, filename):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.post(
            f"/api/images/upload/{image_type}",
            files={"file": (filename, b"\xff\xd8\xff-fake-jpeg", "image/jpeg")},
        )


@pytest.mark.asyncio
async def test_upload_marks_question_verified_when_only_question_image_needed(image_dirs):
    q = _FakeQuestion("g4_q_1")
    session = _FakeSession([q])
    resp = await _upload(_build_app(session), "questions", "g4_q_1.jpg")
    assert resp.status_code == 200, resp.text
    assert resp.json()["verified_questions"] == 1
    assert q.images_verified is True
    assert session.committed is True


@pytest.mark.asyncio
async def test_upload_not_verified_when_answer_image_still_missing(image_dirs):
    q = _FakeQuestion("g4_q_2", answer_image="g4_a_2")
    session = _FakeSession([q])
    resp = await _upload(_build_app(session), "questions", "g4_q_2.jpg")
    assert resp.status_code == 200
    assert resp.json()["verified_questions"] == 0
    assert q.images_verified is False


@pytest.mark.asyncio
async def test_uploading_answer_image_completes_verification(image_dirs):
    q_dir, _ = image_dirs
    (q_dir / "g4_q_3.png").write_bytes(b"png")  # 題目圖已在
    q = _FakeQuestion("g4_q_3", answer_image="g4_a_3")
    session = _FakeSession([q])
    resp = await _upload(_build_app(session), "answers", "g4_a_3.jpg")
    assert resp.status_code == 200
    assert resp.json()["verified_questions"] == 1
    assert q.images_verified is True


@pytest.mark.asyncio
async def test_upload_still_succeeds_when_db_fails(image_dirs):
    class _BrokenSession(_FakeSession):
        async def execute(self, stmt):
            raise RuntimeError("db down")

    resp = await _upload(_build_app(_BrokenSession([])), "questions", "g4_q_4.jpg")
    assert resp.status_code == 200
    assert resp.json()["verified_questions"] == 0
