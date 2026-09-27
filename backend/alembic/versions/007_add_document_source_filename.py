"""Add documents.source_filename

教師回饋:重新上傳同一份 Excel/文字檔時無法追蹤來源,也無法知道哪些文件
來自同一次匯入。新增 documents.source_filename 記錄上傳來源檔名，
供 GET /api/documents/sources 依來源檔名分組，以及重新上傳比對是否取代既有文件。

Revision ID: 007_add_document_source_filename
Revises: 006_fix_template_stem_key
"""
from typing import Union

import sqlalchemy as sa

from alembic import op

revision: str = "007_add_document_source_filename"
down_revision: Union[str, None] = "006_fix_template_stem_key"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("source_filename", sa.String(length=255), nullable=True),
    )
    # 冪等:init.sql 也用 IF NOT EXISTS 建同名索引,兩條路徑交錯時不會撞
    op.create_index(
        "idx_documents_source_filename",
        "documents",
        ["source_filename"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index(
        "idx_documents_source_filename", table_name="documents", if_exists=True
    )
    op.drop_column("documents", "source_filename")
