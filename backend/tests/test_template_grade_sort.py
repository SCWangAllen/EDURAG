"""TemplateService._apply_sort(sort="grade") 編出的 ORDER BY 型別測試。

透過 compile(literal_binds=True) 把 ORDER BY 轉成 SQL 文字驗證：年級排序取
grades JSON 陣列第一個元素的文字值（`->> 0`）與 GRADE_SORT_INDEX 做 simple
CASE 值比對，而不是用 `@>` containment 搭配裸字面值——後者在 asyncpg 上會被
綁成 VARCHAR，撞上 postgres 的 `operator does not exist: jsonb @> character
varying`（真實 DB 才會炸，mock 模式測試不會發現）。
"""
from sqlalchemy import select
from sqlalchemy.dialects import postgresql

from app.db.models import Template
from app.services.template_service import TemplateService


def _compiled_grade_sort_sql() -> str:
    service = TemplateService.__new__(TemplateService)  # 不需要 db session
    query = service._apply_sort(select(Template), "grade")
    return str(
        query.compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
        )
    )


def test_grade_sort_extracts_first_array_element_as_text():
    sql = _compiled_grade_sort_sql()
    assert "->> 0" in sql


def test_grade_sort_does_not_use_untyped_jsonb_containment():
    """`@> '...'`（裸字面值、無 cast）是觸發 jsonb @> character varying 型別
    錯誤的寫法；grade 排序不應再使用它（_apply_filters 的篩選用法不受影響）。"""
    sql = _compiled_grade_sort_sql()
    assert "@> '" not in sql


def test_grade_sort_orders_bands_correctly():
    """CASE 分支依 band 順序排列：ESL → 年級班 → 國中班 → ALL 最後。"""
    sql = _compiled_grade_sort_sql()
    k1_pos = sql.index("WHEN 'K1'")
    g1_pos = sql.index("WHEN 'G1'")
    jr4_pos = sql.index("WHEN 'JR4'")
    all_pos = sql.index("WHEN 'ALL'")
    assert k1_pos < g1_pos < jr4_pos < all_pos
