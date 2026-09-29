"""Add image_questions.source_filename + import_batch_id index

背景:正式站發現 Excel 匯入的圖片名稱與實際上傳檔案不一致(sanitize 規則不同,
見 app/core/image_names.py),老師想知道某道題目/某批題目是從哪個 Excel
匯入的，以便重新匯入或比對來源。新增 image_questions.source_filename 記錄
上傳來源 Excel 檔名，供 GET /api/image-questions/import-batches 顯示與
DELETE /api/image-questions/import-batches/{batch_id} 整批清理使用。

import_batch_id 原本沒有索引，匯入批次清單/刪除都會依此欄位 GROUP BY /
WHERE，一併補上索引。

Revision ID: 010_add_iq_source_filename  (revision id 需 ≤ 32 字元:alembic_version.version_num 是 VARCHAR(32))
Revises: 009_add_template_sort_order
"""
from typing import Union

import sqlalchemy as sa

from alembic import op

revision: str = "010_add_iq_source_filename"
down_revision: Union[str, None] = "009_add_template_sort_order"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "image_questions",
        sa.Column("source_filename", sa.String(length=255), nullable=True),
    )
    # 冪等:init.sql 也用 IF NOT EXISTS 建同名索引,兩條路徑交錯時不會撞
    op.create_index(
        "idx_image_questions_import_batch",
        "image_questions",
        ["import_batch_id"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index(
        "idx_image_questions_import_batch",
        table_name="image_questions",
        if_exists=True,
    )
    op.drop_column("image_questions", "source_filename")
