"""Add app_settings key-value table (stores active LLM model).

Revision ID: 005_add_app_settings
Revises: 004_chapter_to_text
"""
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "005_add_app_settings"
down_revision: Union[str, None] = "004_chapter_to_text"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 冪等:真實模式啟動的 Base.metadata.create_all 可能已先建此表，
    # 存在就跳過，避免 DuplicateTableError。
    conn = op.get_bind()
    if inspect(conn).has_table("app_settings"):
        return
    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(length=64), primary_key=True),
        sa.Column("value", sa.String(length=255), nullable=True),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("app_settings")
