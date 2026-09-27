"""科目刪除守門與軟刪除復活的回歸測試(不需 DB:以假 session 攔截 SQL)。

Bug 背景:科目改成「名稱 + 年級」各一列後,「有沒有範本在用」仍用名稱比對,
新增的年級列被同名其他列的範本牽連而刪不掉;而軟刪除留下的幽靈列又擋住
同名同年級再新增。
"""
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import select
from sqlalchemy.dialects import postgresql

from app.db.models import Subject, Template
from app.schemas.subject import SubjectCreate, SubjectUpdate
from app.services.subject_service import SubjectService


def _subject(sid, name, grade, active=True):
    s = Subject()
    s.id, s.name, s.grade, s.is_active = sid, name, grade, active
    s.color, s.description = "#000000", ""
    return s


def _sql(stmt) -> str:
    return str(
        stmt.compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
        )
    )


def test_grade_row_usage_is_by_subject_id_not_name():
    """年級列(health G3)只認 subject_id,不再被同名範本牽連。"""
    cond = SubjectService.template_usage_condition(_subject(24, "health", "G3"))
    sql = _sql(select(Template).where(cond))
    assert "templates.subject_id = 24" in sql
    assert "templates.subject = 'health'" not in sql


@pytest.mark.parametrize("grade", ["", None, "ALL"])
def test_subject_level_row_still_owns_legacy_name_only_templates(grade):
    """科目層級列(無年級 / ALL)仍歸屬舊的、只存名稱的範本,避免誤刪。"""
    cond = SubjectService.template_usage_condition(_subject(14, "health", grade))
    sql = _sql(select(Template).where(cond))
    assert "templates.subject_id = 14" in sql
    assert "templates.subject_id IS NULL" in sql
    assert "templates.subject = 'health'" in sql


@pytest.mark.asyncio
async def test_count_query_for_grade_row_ignores_name_only_templates():
    captured = {}

    async def fake_execute(stmt):
        captured["sql"] = _sql(stmt)
        result = MagicMock()
        result.scalar.return_value = 0
        return result

    db = MagicMock()
    db.execute = fake_execute
    n = await SubjectService(db)._count_templates_using_subject(
        _subject(24, "health", "G3")
    )
    assert n == 0
    assert "templates.subject_id = 24" in captured["sql"]
    assert "templates.subject = 'health'" not in captured["sql"]


@pytest.mark.asyncio
async def test_usage_stats_keyed_by_row_id():
    """統計以列 id 當 key;同名不同年級各自一筆,不再互相覆蓋。"""
    db = MagicMock()
    svc = SubjectService(db)
    svc.get_subjects = AsyncMock(
        return_value=[_subject(1, "health", "G5-G6"), _subject(24, "health", "G3")]
    )
    svc._count_templates_using_subject = AsyncMock(side_effect=[3, 0])
    stats = await svc.get_subject_usage_stats()
    assert set(stats) == {1, 24}
    assert stats[1]["template_count"] == 3
    assert stats[24]["template_count"] == 0
    assert stats[24]["grade"] == "G3"


@pytest.mark.asyncio
async def test_template_counts_by_name_groups_active_templates():
    """科目層級顯示用:依名稱統計啟用中範本(含舊的只存名稱範本)。"""
    captured = {}

    async def fake_execute(stmt):
        captured["sql"] = _sql(stmt)
        result = MagicMock()
        result.all.return_value = [("health", 7), ("math", 2), (None, 1)]
        return result

    db = MagicMock()
    db.execute = fake_execute
    counts = await SubjectService(db).get_template_counts_by_name()
    assert counts == {"health": 7, "math": 2}
    assert "GROUP BY templates.subject" in captured["sql"]
    assert "templates.is_active IS true" in captured["sql"]


def _mock_db():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_create_reactivates_soft_deleted_same_name_grade():
    ghost = _subject(9, "zz_probe", "G1", active=False)
    db = _mock_db()
    svc = SubjectService(db)
    svc.get_subject_by_name_and_grade = AsyncMock(return_value=ghost)

    result = await svc.create_subject(
        SubjectCreate(name="zz_probe", grade="G1", description="new", color="#123456")
    )

    assert result is ghost
    assert ghost.is_active is True
    assert ghost.description == "new"
    assert ghost.color == "#123456"
    db.add.assert_not_called()
    db.commit.assert_awaited()


@pytest.mark.asyncio
async def test_create_still_rejects_active_duplicate():
    live = _subject(9, "zz_probe", "G1", active=True)
    db = _mock_db()
    svc = SubjectService(db)
    svc.get_subject_by_name_and_grade = AsyncMock(return_value=live)

    with pytest.raises(ValueError, match="已經有年級 G1"):
        await svc.create_subject(SubjectCreate(name="zz_probe", grade="G1"))
    db.add.assert_not_called()


@pytest.mark.asyncio
async def test_update_rejects_grade_collision_with_actionable_message():
    """科目改年級撞到既有 (name, grade) 時，訊息要導去模板編輯的「適用年級」，
    而不是暗示要改科目本身（科目與年級是各自獨立的維度）。"""
    current = _subject(9, "health", "G1", active=True)
    other = _subject(10, "health", "G2", active=True)
    db = _mock_db()
    svc = SubjectService(db)
    svc.get_subject_by_id = AsyncMock(return_value=current)
    svc.get_subject_by_name_and_grade = AsyncMock(return_value=other)

    with pytest.raises(ValueError, match="已經有年級 G2") as exc_info:
        await svc.update_subject(9, SubjectUpdate(grade="G2"))

    message = str(exc_info.value)
    assert "適用年級" in message
    assert "不需要修改科目本身" in message


def test_duplicate_subject_message_handles_blank_grade():
    """grade 為空（不分年級）時訊息仍可讀，不會出現「已經有年級 」的斷尾。"""
    message = SubjectService.duplicate_subject_message("health", "")
    assert "已經有年級 （不分年級）" in message
    assert "適用年級" in message
