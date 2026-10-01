"""blank_count(圖片上的作答空格數，計分用):schema 驗證 + Excel 匯入解析。

沿用 test_image_question_dedupe.py 的做法:只測純函式/schema,不碰 DB。
"""
from io import BytesIO

import pandas as pd
import pytest
from pydantic import ValidationError

from app.schemas.image_question import ImageQuestionCreate
from app.services.image_question_service import ImageQuestionService, parse_blank_count

# --- schema ---------------------------------------------------------------


def _create_kwargs(**overrides):
    kwargs = {"question_image": "g4_q_1", "subject": "Health"}
    kwargs.update(overrides)
    return kwargs


def test_blank_count_defaults_to_one():
    data = ImageQuestionCreate(**_create_kwargs())
    assert data.blank_count == 1


def test_blank_count_accepts_positive_value():
    data = ImageQuestionCreate(**_create_kwargs(blank_count=3))
    assert data.blank_count == 3


def test_blank_count_zero_is_rejected():
    with pytest.raises(ValidationError):
        ImageQuestionCreate(**_create_kwargs(blank_count=0))


def test_blank_count_above_max_is_rejected():
    with pytest.raises(ValidationError):
        ImageQuestionCreate(**_create_kwargs(blank_count=51))


# --- parse_blank_count(純函式) --------------------------------------------


def test_parse_blank_count_missing_defaults_to_one():
    assert parse_blank_count(None) == (1, None)


def test_parse_blank_count_blank_string_defaults_to_one():
    assert parse_blank_count("") == (1, None)
    assert parse_blank_count("nan") == (1, None)


def test_parse_blank_count_valid_string_number():
    assert parse_blank_count("3") == (3, None)


def test_parse_blank_count_valid_float_like_excel_cell():
    # Excel 數字欄位讀進 pandas 常是 float(例如 3.0)
    assert parse_blank_count(3.0) == (3, None)


def test_parse_blank_count_non_numeric_defaults_to_one_with_warning():
    count, warning = parse_blank_count("abc")
    assert count == 1
    assert warning is not None


def test_parse_blank_count_zero_or_negative_defaults_to_one_with_warning():
    assert parse_blank_count(0)[0] == 1
    assert parse_blank_count(0)[1] is not None
    assert parse_blank_count(-2)[0] == 1
    assert parse_blank_count(-2)[1] is not None


# --- parse_excel(端到端,僅操作記憶體中的 xlsx,不碰 DB/檔案系統) -----------


def _build_xlsx(rows: list[dict]) -> bytes:
    df = pd.DataFrame(rows)
    buf = BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    return buf.getvalue()


def test_parse_excel_blanks_column_is_honoured():
    contents = _build_xlsx([{"q_image": "g4_q_1", "subject": "Health", "Blanks": 3}])
    service = ImageQuestionService(db=None)
    preview = service.parse_excel(contents, "test.xlsx")
    assert preview.items[0].blank_count == 3


def test_parse_excel_missing_blanks_column_defaults_to_one():
    contents = _build_xlsx([{"q_image": "g4_q_1", "subject": "Health"}])
    service = ImageQuestionService(db=None)
    preview = service.parse_excel(contents, "test.xlsx")
    assert preview.items[0].blank_count == 1


def test_parse_excel_non_numeric_blanks_defaults_to_one_with_warning():
    contents = _build_xlsx(
        [{"q_image": "g4_q_1", "subject": "Health", "Blanks": "abc"}]
    )
    service = ImageQuestionService(db=None)
    preview = service.parse_excel(contents, "test.xlsx")
    assert preview.items[0].blank_count == 1
    assert any("Blanks" in w and "1" in w for w in preview.warnings)
