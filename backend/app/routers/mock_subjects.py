"""Mock 科目 API — 回傳與真實 /api/subjects 相同 schema 的靜態資料。

Mock 模式（USE_MOCK_API=true）下由 main.py 掛載；不需 DB。
科目名稱使用 canonical 英文小寫 key。
"""
from types import SimpleNamespace

from fastapi import APIRouter, HTTPException

from app.services.subject_service import build_subject_tree

router = APIRouter(prefix="/api/subjects", tags=["subjects"])

_FIXED_TS = "2024-01-01T00:00:00Z"

# (id, name, grade, color, description)；health 有多年級列以覆蓋樹狀聚合
_MOCK_SUBJECT_ROWS = [
    (1, "health", "ALL", "#10B981", "健康教育相關內容"),
    (2, "health", "G4", "#10B981", "健康教育相關內容"),
    (3, "english", "ALL", "#3B82F6", "英語學習相關內容"),
    (4, "history", "ALL", "#F59E0B", "歷史知識相關內容"),
    (5, "math", "ALL", "#EF4444", "數學相關內容"),
]


def _subject_dict(row):
    sid, name, grade, color, description = row
    return {
        "id": sid,
        "name": name,
        "grade": grade,
        "color": color,
        "description": description,
        "is_active": True,
        "created_at": _FIXED_TS,
        "updated_at": _FIXED_TS,
    }


@router.get("/")
async def get_subjects_mock(include_inactive: bool = False):
    """取得科目清單 (Mock 模式)"""
    subjects = [_subject_dict(row) for row in _MOCK_SUBJECT_ROWS]
    return {"subjects": subjects, "total": len(subjects)}


@router.get("/tree")
async def get_subject_tree_mock():
    """取得 科目→年級 樹 (Mock 模式)"""
    rows = [
        SimpleNamespace(id=sid, name=name, grade=grade, color=color)
        for sid, name, grade, color, _ in _MOCK_SUBJECT_ROWS
    ]
    tree = build_subject_tree(rows)
    return {"subjects": tree, "total": len(tree)}


@router.get("/usage/stats")
async def get_subject_usage_stats_mock():
    """取得科目使用統計 (Mock 模式)"""
    return {"stats": []}


# 注意：/{subject_id} 必須在 /tree、/usage/stats 之後註冊
@router.get("/{subject_id}")
async def get_subject_mock(subject_id: int):
    """取得單一科目 (Mock 模式)"""
    for row in _MOCK_SUBJECT_ROWS:
        if row[0] == subject_id:
            return _subject_dict(row)
    raise HTTPException(status_code=404, detail=f"科目 ID {subject_id} 不存在")


@router.post("/", status_code=201)
async def create_subject_mock(subject_data: dict):
    """建立科目 (Mock 模式) — 回傳與真實 schema 相同結構，不持久化"""
    return {
        "id": 999,
        "name": subject_data.get("name", ""),
        "grade": subject_data.get("grade", ""),
        "color": subject_data.get("color", "#3B82F6"),
        "description": subject_data.get("description"),
        "is_active": True,
        "created_at": _FIXED_TS,
        "updated_at": _FIXED_TS,
    }


@router.put("/{subject_id}")
async def update_subject_mock(subject_id: int, subject_data: dict):
    """更新科目 (Mock 模式) — 回傳合併後結構，不持久化"""
    for row in _MOCK_SUBJECT_ROWS:
        if row[0] == subject_id:
            merged = _subject_dict(row)
            merged.update({k: v for k, v in subject_data.items() if v is not None})
            return merged
    raise HTTPException(status_code=404, detail=f"科目 ID {subject_id} 不存在")


@router.delete("/{subject_id}")
async def delete_subject_mock(subject_id: int, force: bool = False):
    """刪除科目 (Mock 模式) — 不持久化"""
    return {"message": f"科目已{'強制' if force else ''}刪除"}
