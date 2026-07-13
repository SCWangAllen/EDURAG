"""documents.chapter VARCHAR(100) -> TEXT.

超過 100 字的章節在 Excel 匯入時觸發 StringDataRightTruncation，
且錯誤被靜默吞掉導致整筆文件未入庫（使用者回饋「超過 100 字被刪除」）。

Revision ID: 004_chapter_to_text
Revises: 003_normalize_subject_grade
"""
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_chapter_to_text"
down_revision: Union[str, None] = "003_normalize_subject_grade"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "documents",
        "chapter",
        existing_type=sa.String(length=100),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    # 注意：降級會把超過 100 字的 chapter 截斷（lossy）
    op.execute("UPDATE documents SET chapter = left(chapter, 100) WHERE length(chapter) > 100")
    op.alter_column(
        "documents",
        "chapter",
        existing_type=sa.Text(),
        type_=sa.String(length=100),
        existing_nullable=True,
    )
