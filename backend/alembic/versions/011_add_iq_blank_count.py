"""Add image_questions.blank_count

背景:出題紙需要依圖片題目的「作答空格數」計分(例如一張圖有 3 個空格要填,
就該算 3 分),但現行 image_questions 完全不知道一張圖有幾個空格。新增
blank_count 欄位記錄此數值,預設 1(維持舊資料/舊匯入流程行為不變)。

Revision ID: 011_add_iq_blank_count  (revision id 需 ≤ 32 字元:alembic_version.version_num 是 VARCHAR(32))
Revises: 010_add_iq_source_filename
"""
from typing import Union

import sqlalchemy as sa

from alembic import op

revision: str = "011_add_iq_blank_count"
down_revision: Union[str, None] = "010_add_iq_source_filename"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "image_questions",
        sa.Column(
            "blank_count",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )


def downgrade() -> None:
    op.drop_column("image_questions", "blank_count")
