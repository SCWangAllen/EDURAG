"""正規化圖片名稱(純函式):Excel 只 strip(),但圖片上傳端點會清理特殊字元
且不接受副檔名,兩邊規則不一致造成同一張圖被判定成兩個不同名稱。"""
from app.core.image_names import normalize_image_name


def test_replaces_disallowed_characters_with_underscore():
    assert normalize_image_name("a b.1") == "a_b_1"


def test_strips_trailing_extension_case_insensitively():
    assert normalize_image_name("x.PNG") == "x"


def test_only_strips_one_trailing_extension():
    assert normalize_image_name("x.png.png") == "x_png"


def test_strips_surrounding_whitespace():
    assert normalize_image_name(" y ") == "y"


def test_none_returns_empty_string():
    assert normalize_image_name(None) == ""


def test_empty_or_blank_string_returns_empty_string():
    assert normalize_image_name("") == ""
    assert normalize_image_name("   ") == ""


def test_already_clean_name_is_unchanged():
    assert normalize_image_name("g4_question_health_v4_5_image01") == (
        "g4_question_health_v4_5_image01"
    )


def test_supports_all_recognized_extensions():
    for ext in ("jpg", "jpeg", "png", "webp", "gif"):
        assert normalize_image_name(f"photo.{ext}") == "photo"


def test_schema_rejects_empty_question_image_after_normalization():
    import pytest
    from pydantic import ValidationError

    from app.schemas.image_question import ImageQuestionCreate, ImageQuestionUpdate

    with pytest.raises(ValidationError):
        ImageQuestionUpdate(question_image=".png")
    with pytest.raises(ValidationError):
        ImageQuestionCreate(question_image="  ", subject="health")
    assert ImageQuestionUpdate(question_image="a b.1").question_image == "a_b_1"
