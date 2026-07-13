"""Normalize subject names to canonical english keys and grade casing.

Canonical 科目名 = 英文小寫 key（health/english/...）。
本 migration 為純資料遷移（無 schema 變更）：
- documents.subject / templates.subject / image_questions.subject / subjects.name
  之中文與首大寫英文別名 → canonical key
- questions.source_metadata 的 subject / grade key 同步改寫
- grade 大小寫收斂（g4→G4、all→ALL；未知值保留不動，避免不可逆資料毀損）
- subjects 表合併防撞：別名列與 canonical 列 (name, grade) 相同時，
  先把 templates.subject_id 重指到保留列，再刪除重複列

Revision ID: 003_normalize_subject_grade
Revises: 002_subject_grade_decouple
"""
from typing import Union

from alembic import op

revision: str = "003_normalize_subject_grade"
down_revision: Union[str, None] = "002_subject_grade_decouple"
branch_labels = None
depends_on = None

# canonical key → 舊別名（中文 / 首大寫 / 全大寫）
CANONICAL_ALIASES = {
    "health": ["健康", "Health", "HEALTH"],
    "english": ["英文", "English", "ENGLISH"],
    "history": ["歷史", "History", "HISTORY"],
    "math": ["數學", "Math", "MATH"],
    "science": ["自然", "Science", "SCIENCE"],
    "chinese": ["國文", "Chinese", "CHINESE"],
    "social": ["社會", "Social", "SOCIAL"],
}

VALID_GRADES_SQL = "('G1','G2','G3','G4','G5','G6','ALL')"


def _quoted(values):
    return ", ".join("'{}'".format(v) for v in values)


def _repoint_templates(alias: str, canon: str) -> str:
    """把指向別名科目列的 templates.subject_id 重指到同 grade 的 canonical 列。"""
    return f"""
        UPDATE templates t SET subject_id = keep.id
        FROM subjects dup, subjects keep
        WHERE t.subject_id = dup.id
          AND dup.name = '{alias}'
          AND keep.name = '{canon}'
          AND COALESCE(keep.grade, '') = COALESCE(dup.grade, '')
    """


def _rename_subject_rows(alias: str, canon: str) -> str:
    """無撞名（同 name+grade）疑慮的別名列直接改名。"""
    return f"""
        UPDATE subjects s SET name = '{canon}'
        WHERE s.name = '{alias}'
          AND NOT EXISTS (
              SELECT 1 FROM subjects k
              WHERE k.name = '{canon}'
                AND COALESCE(k.grade, '') = COALESCE(s.grade, '')
          )
    """


def upgrade() -> None:
    for canon, aliases in CANONICAL_ALIASES.items():
        alias_list = _quoted(aliases)

        # 純字串欄位
        op.execute(
            f"UPDATE documents SET subject = '{canon}' WHERE subject IN ({alias_list})"
        )
        op.execute(
            f"UPDATE templates SET subject = '{canon}' WHERE subject IN ({alias_list})"
        )
        op.execute(
            "UPDATE image_questions SET subject = '{0}' WHERE subject IN ({1})".format(
                canon, alias_list
            )
        )

        # questions.source_metadata JSON 內的 subject
        op.execute(
            f"""
            UPDATE questions
            SET source_metadata = jsonb_set(
                source_metadata::jsonb, '{{subject}}', to_jsonb('{canon}'::text)
            )::json
            WHERE source_metadata->>'subject' IN ({alias_list})
        """
        )

        # subjects 表：逐別名處理，避免 (name, grade) 複合唯一撞名
        for alias in aliases:
            op.execute(_repoint_templates(alias, canon))
            op.execute(_rename_subject_rows(alias, canon))
            op.execute(_repoint_templates(alias, canon))
        op.execute(f"DELETE FROM subjects WHERE name IN ({alias_list})")

    # grade 大小寫/空白收斂（僅已知值域；未知值保留）
    for table in ("documents", "subjects", "image_questions"):
        op.execute(
            f"""
            UPDATE {table} SET grade = upper(trim(grade))
            WHERE grade IS NOT NULL
              AND upper(trim(grade)) IN {VALID_GRADES_SQL}
              AND grade <> upper(trim(grade))
        """
        )
    op.execute(
        f"""
        UPDATE questions
        SET source_metadata = jsonb_set(
            source_metadata::jsonb, '{{grade}}',
            to_jsonb(upper(trim(source_metadata->>'grade')))
        )::json
        WHERE source_metadata->>'grade' IS NOT NULL
          AND upper(trim(source_metadata->>'grade')) IN {VALID_GRADES_SQL}
          AND source_metadata->>'grade' <> upper(trim(source_metadata->>'grade'))
    """
    )


def downgrade() -> None:
    """Best-effort 還原為中文主別名。

    注意：upgrade 中被合併刪除的重複 subjects 列無法還原（lossy）。
    """
    for canon, aliases in CANONICAL_ALIASES.items():
        zh = aliases[0]  # 主別名 = 中文
        op.execute(f"UPDATE documents SET subject = '{zh}' WHERE subject = '{canon}'")
        op.execute(f"UPDATE templates SET subject = '{zh}' WHERE subject = '{canon}'")
        op.execute(
            f"UPDATE image_questions SET subject = '{zh}' WHERE subject = '{canon}'"
        )
        op.execute(
            f"""
            UPDATE questions
            SET source_metadata = jsonb_set(
                source_metadata::jsonb, '{{subject}}', to_jsonb('{zh}'::text)
            )::json
            WHERE source_metadata->>'subject' = '{canon}'
        """
        )
        op.execute(f"UPDATE subjects SET name = '{zh}' WHERE name = '{canon}'")
