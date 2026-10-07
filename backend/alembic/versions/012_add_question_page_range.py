"""Add questions.page_from / page_to（題目自己記的課本頁碼範圍）

背景:題目原本只掛「這次勾選的第一份教材」(document_id),列表顯示的頁碼是 join
那份教材讀來的。老師一次勾很多份教材生題時,整批題目都會顯示第一份的頁碼
(線上 214 題裡 60 題掛在整個教材庫排第一的健康 G4 第一章 P.1-3,歷史題也掛在上面)。
現在存題時由前端依「這次勾選的全部教材」算出最小起、最大迄存進題目自己身上,
篩選改用「包含」語意(app.core.page_range.page_containment_conditions)。

回填:既有題目依 document_id 對應教材的 page_number 解析出範圍(規則與當時的
app.core.page_range.page_bounds 相同,但這裡是凍結的字面值,之後改 page_range 不會
改變這支 migration 的行為)。注意顯示會從「教材頁碼原文」變成「解析後的範圍」:
"pp. 115-171" 顯示成 115-171;解析不出來的(例如 "xxii")或超出 CHECK 範圍
(1–1,000,000,例如頁碼欄填了 ISBN)維持 NULL,挑題清單不再顯示頁碼。

Revision ID: 012_add_question_page_range  (≤ 32 字元)
Revises: 011_add_iq_blank_count
"""
from typing import Union

import sqlalchemy as sa

from alembic import op

revision: str = "012_add_question_page_range"
down_revision: Union[str, None] = "011_add_iq_blank_count"
branch_labels = None
depends_on = None

PAGE_MAX = 1_000_000

# 解析規則的凍結快照(與撰寫當時的 app.core.page_range 相同;刻意不 import app 程式碼,
# migration 的行為不該隨日後調整篩選規則而改變):全形數字→半形、去掉貼在數字後面的小數、
# 第一個數字當起、最後一個數字當迄(NUMERIC,避免超長數字串 cast INTEGER 溢位)
_FULLWIDTH_DIGITS = "０１２３４５６７８９"
_HALFWIDTH_DIGITS = "0123456789"
_SQL_DECIMAL_SUFFIX_PATTERN = r"(?<=\d)\.\d+"
_SQL_FIRST_NUMBER_PATTERN = r"(\d+)"
_SQL_LAST_NUMBER_PATTERN = r"(\d+)\D*$"

BACKFILL_SQL = f"""
WITH parsed AS (
    SELECT
        d.id AS document_id,
        CAST(substring(cleaned FROM '{_SQL_FIRST_NUMBER_PATTERN}') AS NUMERIC) AS start_page,
        COALESCE(
            CAST(substring(cleaned FROM '{_SQL_LAST_NUMBER_PATTERN}') AS NUMERIC),
            CAST(substring(cleaned FROM '{_SQL_FIRST_NUMBER_PATTERN}') AS NUMERIC)
        ) AS end_page
    FROM (
        SELECT id,
               regexp_replace(
                   translate(page_number, '{_FULLWIDTH_DIGITS}', '{_HALFWIDTH_DIGITS}'),
                   '{_SQL_DECIMAL_SUFFIX_PATTERN}', '', 'g'
               ) AS cleaned
        FROM documents
        WHERE page_number IS NOT NULL
    ) d
)
UPDATE questions q
SET page_from = LEAST(p.start_page, p.end_page)::INTEGER,
    page_to   = GREATEST(p.start_page, p.end_page)::INTEGER
FROM parsed p
WHERE q.document_id = p.document_id
  AND q.page_from IS NULL
  AND p.start_page IS NOT NULL
  AND LEAST(p.start_page, p.end_page) >= 1
  AND GREATEST(p.start_page, p.end_page) <= {PAGE_MAX}
"""


def upgrade() -> None:
    op.add_column("questions", sa.Column("page_from", sa.Integer(), nullable=True))
    op.add_column("questions", sa.Column("page_to", sa.Integer(), nullable=True))
    op.create_check_constraint(
        "ck_questions_page_range",
        "questions",
        "(page_from IS NULL AND page_to IS NULL) OR "
        f"(page_from >= 1 AND page_to >= page_from AND page_to <= {PAGE_MAX})",
    )
    op.create_index("ix_questions_page_from_to", "questions", ["page_from", "page_to"])
    op.execute(BACKFILL_SQL)


def downgrade() -> None:
    op.drop_index("ix_questions_page_from_to", table_name="questions")
    op.drop_constraint("ck_questions_page_range", "questions", type_="check")
    op.drop_column("questions", "page_to")
    op.drop_column("questions", "page_from")
