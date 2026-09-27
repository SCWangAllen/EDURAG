"""Drop legacy grade CHECK constraints (G1-G6/ALL only)

新年級白名單（ESL K1/K2/A1/A2、國中班 JR4-JR9、既有 G1-G6、ALL）已改由
app.core.subject_norm.VALID_GRADES 統一驗證。部分較舊的資料庫（沿用 2.x 之前
init 腳本建置的環境）仍留著資料庫層的 CHECK 約束，只允許 'G1'..'G6'/'ALL'，
導致寫入新代碼（例如 JR4）時觸發 CheckViolationError（見 POST /api/documents/copy
複製到 JR4 年級時的 500）。db/init.sql 目前已不含這些約束，僅為保護仍帶有
舊約束的既有資料庫而新增本 migration；沒有該約束的資料庫執行 IF EXISTS 為
no-op，安全可重複執行。

Revision ID: 008_drop_grade_check_constraints
Revises: 007_add_document_source_filename
"""
from typing import Union

from alembic import op

revision: str = "008_drop_grade_check_constraints"
down_revision: Union[str, None] = "007_add_document_source_filename"
branch_labels = None
depends_on = None

# 四張表舊有的 grade CHECK 約束名稱（來自 2.x 之前的 init 腳本；目前 init.sql
# 已不建立這些約束，這裡逐一 DROP IF EXISTS 只為相容仍殘留約束的舊資料庫）
_GRADE_CHECK_CONSTRAINTS = {
    "documents": "check_documents_grade",
    "subjects": "check_subjects_grade",
    "image_questions": "check_image_questions_grade",
    "questions": "check_questions_grade",
}


def upgrade() -> None:
    # DROP CONSTRAINT IF EXISTS 不會保護「表不存在」的情況(舊 DB 可能還沒有 image_questions),
    # 用 to_regclass 先確認表存在再動手
    for table, constraint in _GRADE_CHECK_CONSTRAINTS.items():
        op.execute(
            f"""
            DO $$
            BEGIN
                IF to_regclass('public.{table}') IS NOT NULL THEN
                    ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {constraint};
                END IF;
            END $$;
            """
        )


def downgrade() -> None:
    # No-op：舊約束只允許 'G1'..'G6'/'ALL'，重建它會讓 ESL（K1/K2/A1/A2）與
    # 國中班（JR4-JR9）代碼全部寫入失敗，故刻意不還原。
    pass
