"""Add templates.sort_order for manual ordering

教師回饋:模板清單只能依科目/年級/建立時間排序,老師想把常用的模板拖到前面、
把不常用的往後放。新增 templates.sort_order(NULL-able)供 GET /api/templates/
的 sort=manual 排序,以及 POST /api/templates/{id}/move 上移/下移使用。

NULL 代表尚未手動排序過;第一次呼叫 move 時,service 層會依當下顯示順序
(sort_order ASC NULLS LAST, created_at DESC, id ASC)一次性指派
sort_order = index * 10,把目前順序「凍結」下來,之後的上移/下移都在這個
基準上互換 —— 不需要在這裡補一次資料回填。

Revision ID: 009_add_template_sort_order
Revises: 008_drop_grade_check_constraints
"""
from typing import Union

import sqlalchemy as sa

from alembic import op

revision: str = "009_add_template_sort_order"
down_revision: Union[str, None] = "008_drop_grade_check_constraints"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "templates",
        sa.Column("sort_order", sa.Integer(), nullable=True),
    )
    # 冪等:init.sql 也用 IF NOT EXISTS 建同名索引,兩條路徑交錯時不會撞
    op.create_index(
        "idx_templates_sort_order",
        "templates",
        ["sort_order"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index("idx_templates_sort_order", table_name="templates", if_exists=True)
    op.drop_column("templates", "sort_order")
