"""build_template_subject_filter 是純函式（回傳 SQLAlchemy 條件，不觸 DB）。

透過 compile(literal_binds=True) 把條件轉成 SQL 文字，驗證：
1. 大小寫/前後空白不敏感（正規化後一律比對小寫值）。
2. 已知中文別名會被 normalize_subject() 轉成 canonical 英文 key 再比對，
   而不是把原始中文字串直接送進 SQL（修正教師回饋的篩選 bug）。
"""
from sqlalchemy.dialects import postgresql

from app.services.template_service import build_template_subject_filter


def _compiled_sql(subject: str) -> str:
    clause = build_template_subject_filter(subject)
    return str(
        clause.compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
        )
    )


def test_known_chinese_alias_normalizes_to_canonical_english_key():
    sql = _compiled_sql("健康")
    assert "'health'" in sql
    assert "健康" not in sql


def test_titlecase_and_uppercase_normalize_to_same_canonical_value():
    assert "'health'" in _compiled_sql("Health")
    assert "'health'" in _compiled_sql("HEALTH")


def test_whitespace_and_case_insensitive_for_custom_subject():
    # 自訂科目（不在別名表中）：僅正規化大小寫與前後空白，不轉換內容
    sql = _compiled_sql("  Robotics  ")
    assert "'robotics'" in sql


def test_filter_compares_both_subject_column_and_subject_relation():
    """initialize_default_templates 建立的模板沒有 subject_id，
    仍要能靠 subject 文字欄位命中；同時也要能靠關聯 Subject.name 命中。"""
    sql = _compiled_sql("english")
    assert "templates.subject" in sql
    assert "subjects" in sql or "subject_id" in sql or "EXISTS" in sql.upper()
