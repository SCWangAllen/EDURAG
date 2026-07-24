"""Fix template output key: "stem": -> "prompt":

約 15 個 seed 模版的 prompt 指示 AI 輸出 JSON key "stem"，但解析器只接受
"prompt"（llm_client.py 校驗 q.get("prompt")），導致生成的題目全被丟棄。
此 data migration 把現存模版 content 裡的 JSON key "stem": 改為 "prompt":。

Revision ID: 006_fix_template_stem_key
Revises: 005_add_app_settings
"""
from typing import Union

from alembic import op

revision: str = "006_fix_template_stem_key"
down_revision: Union[str, None] = "005_add_app_settings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 精準對 JSON key "stem":（含冒號），不誤傷散文中的 stem
    op.execute(
        """
        UPDATE templates
        SET content = replace(content, '"stem":', '"prompt":')
        WHERE content LIKE '%"stem":%'
        """
    )


def downgrade() -> None:
    # No-op:這是修正壞資料。無法區分哪些模版原本就是正確的 "prompt"，
    # 盲目反向會毀掉本來就正確的模版，故不還原。
    pass
