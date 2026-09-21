"""Excel 匯入去重:同名 question_image 已存在或同批重複的列要被標記並略過(純函式)。"""
from app.schemas.image_question import ImageQuestionPreviewItem
from app.services.image_question_service import mark_duplicates


def _item(row, name, has_error=False):
    return ImageQuestionPreviewItem(row_number=row, question_image=name, subject="health", has_error=has_error)


def test_marks_rows_already_in_db():
    items = [_item(1, "g4_q_1"), _item(2, "g4_q_2"), _item(3, "g4_q_3")]
    assert mark_duplicates(items, {"g4_q_2"}) == 1
    assert [i.is_duplicate for i in items] == [False, True, False]


def test_marks_repeats_within_same_file_keeping_first():
    items = [_item(1, "g4_q_1"), _item(2, "g4_q_1"), _item(3, "g4_q_1")]
    assert mark_duplicates(items, set()) == 2
    assert [i.is_duplicate for i in items] == [False, True, True]


def test_error_rows_are_ignored_and_not_counted():
    items = [_item(1, "g4_q_1", has_error=True), _item(2, "g4_q_1")]
    assert mark_duplicates(items, set()) == 0
    assert items[1].is_duplicate is False


def test_rerun_resets_previous_flags():
    items = [_item(1, "g4_q_1")]
    items[0].is_duplicate = True  # 舊標記
    assert mark_duplicates(items, set()) == 0
    assert items[0].is_duplicate is False
