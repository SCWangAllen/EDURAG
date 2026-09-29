"""匯入批次清單 / 刪除 / GET 清單的 import_batch_id 篩選。

沿用 test_images_delete.py 的做法:掛真 router,但直接覆寫
get_image_question_service(而非 get_db),繞過 Mock 模式下 get_db 回 503
的限制,並讓每個測試拿到一份獨立、可控的 MockImageQuestionService 資料。
"""
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.routers import image_questions as image_questions_module
from app.services.image_question_service import MockImageQuestionService


def _row(id, question_image, import_batch_id, created_at, **overrides):
    """建最小 ImageQuestionResponse 相容的 mock 題目字典(補齊 schema 必要欄位)。"""
    row = {
        "id": id,
        "question_image": question_image,
        "answer_image": None,
        "question_description": None,
        "subject": "Health",
        "chapter": None,
        "grade": None,
        "page": None,
        "question_image_ext": "jpg",
        "answer_image_ext": "jpg",
        "question_image_path": f"{question_image}.jpg",
        "answer_image_path": None,
        "images_verified": False,
        "import_batch_id": import_batch_id,
        "source_filename": None,
        "is_active": True,
        "created_at": created_at,
        "updated_at": created_at,
    }
    row.update(overrides)
    return row


ROWS = [
    # batch_a:2 筆啟用中,1 已驗證 1 未驗證
    _row(
        1,
        "qa1",
        "batch_a",
        "2026-01-01T10:00:00Z",
        source_filename="a.xlsx",
        images_verified=True,
    ),
    _row(
        2,
        "qa2",
        "batch_a",
        "2026-01-01T10:05:00Z",
        answer_image="aa2",
        source_filename="a.xlsx",
    ),
    # batch_b:1 筆啟用中(較晚匯入) + 1 筆已被刪除(不應計入)
    _row(
        3,
        "qb1",
        "batch_b",
        "2026-01-02T09:00:00Z",
        source_filename="b.xlsx",
        images_verified=True,
    ),
    _row(
        4,
        "qb2",
        "batch_b",
        "2026-01-02T09:01:00Z",
        source_filename="b.xlsx",
        is_active=False,
    ),
    # batch_c:整批都已刪除,清單/刪除都不該再看到它
    _row(
        5,
        "qc1",
        "batch_c",
        "2026-01-03T00:00:00Z",
        source_filename="c.xlsx",
        is_active=False,
    ),
]


def _fresh_service() -> MockImageQuestionService:
    service = MockImageQuestionService()
    service.mock_questions = [dict(row) for row in ROWS]
    return service


def _build_app(service):
    app = FastAPI()
    app.include_router(image_questions_module.router)

    async def _override():
        return service

    app.dependency_overrides[
        image_questions_module.get_image_question_service
    ] = _override
    return app


async def _get(app, path, **params):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get(path, params=params or None)


async def _delete(app, path, **params):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.delete(path, params=params or None)


@pytest.mark.asyncio
async def test_list_import_batches_excludes_fully_deleted_batch_and_sorts_desc():
    app = _build_app(_fresh_service())
    resp = await _get(app, "/api/image-questions/import-batches")

    assert resp.status_code == 200, resp.text
    batches = resp.json()["batches"]
    ids = [b["batch_id"] for b in batches]

    # batch_c 全部題目都已刪除,不應出現
    assert "batch_c" not in ids
    # 依 imported_at 新到舊:batch_b(2026-01-02)在 batch_a(2026-01-01)之前
    assert ids == ["batch_b", "batch_a"]


@pytest.mark.asyncio
async def test_list_import_batches_counts_only_active_rows():
    app = _build_app(_fresh_service())
    resp = await _get(app, "/api/image-questions/import-batches")

    batches = {b["batch_id"]: b for b in resp.json()["batches"]}

    # batch_b 有 2 筆但 1 筆已刪除,只算啟用中的 1 筆
    assert batches["batch_b"]["total"] == 1
    assert batches["batch_b"]["verified"] == 1
    assert batches["batch_b"]["missing"] == 0
    assert batches["batch_b"]["source_filename"] == "b.xlsx"

    # batch_a 2 筆都啟用,1 已驗證 1 未驗證
    assert batches["batch_a"]["total"] == 2
    assert batches["batch_a"]["verified"] == 1
    assert batches["batch_a"]["missing"] == 1


@pytest.mark.asyncio
async def test_delete_import_batch_soft_deletes_active_rows():
    service = _fresh_service()
    app = _build_app(service)

    resp = await _delete(app, "/api/image-questions/import-batches/batch_a")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["batch_id"] == "batch_a"
    assert data["deleted_questions"] == 2
    assert data["deleted_images"] == []  # mock 模式不觸碰檔案系統
    assert data["kept_images"] == 3  # qa1, qa2, aa2

    row1 = next(q for q in service.mock_questions if q["id"] == 1)
    row2 = next(q for q in service.mock_questions if q["id"] == 2)
    assert row1["is_active"] is False
    assert row2["is_active"] is False


@pytest.mark.asyncio
async def test_delete_import_batch_missing_returns_404():
    app = _build_app(_fresh_service())
    resp = await _delete(app, "/api/image-questions/import-batches/does-not-exist")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "匯入批次不存在或已無題目"


@pytest.mark.asyncio
async def test_delete_import_batch_already_deleted_returns_404():
    """batch_c 整批題目都已軟刪,再刪一次應視為「已無題目」回 404。"""
    app = _build_app(_fresh_service())
    resp = await _delete(app, "/api/image-questions/import-batches/batch_c")

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_questions_filters_by_import_batch_id():
    app = _build_app(_fresh_service())
    resp = await _get(app, "/api/image-questions/", import_batch_id="batch_a")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total"] == 2
    assert {q["question_image"] for q in data["questions"]} == {"qa1", "qa2"}


@pytest.mark.asyncio
async def test_get_questions_filter_no_match_returns_empty():
    app = _build_app(_fresh_service())
    resp = await _get(app, "/api/image-questions/", import_batch_id="no-such-batch")

    assert resp.status_code == 200
    assert resp.json()["total"] == 0
