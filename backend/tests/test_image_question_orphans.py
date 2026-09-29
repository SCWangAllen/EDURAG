"""plan_orphan_images(純函式):刪除匯入批次時,決定哪些圖片檔可以安全刪除。"""
from app.services.image_question_service import plan_orphan_images


def test_names_not_referenced_elsewhere_are_orphans():
    deleted = {"a", "b", "c"}
    still_referenced = {"b"}
    assert plan_orphan_images(deleted, still_referenced) == {"a", "c"}


def test_all_still_referenced_means_no_orphans():
    deleted = {"a", "b"}
    still_referenced = {"a", "b"}
    assert plan_orphan_images(deleted, still_referenced) == set()


def test_none_still_referenced_means_all_orphans():
    deleted = {"a", "b"}
    still_referenced = set()
    assert plan_orphan_images(deleted, still_referenced) == {"a", "b"}


def test_empty_deleted_set_returns_empty():
    assert plan_orphan_images(set(), {"x"}) == set()


def test_ignores_falsy_names_in_deleted_set():
    deleted = {"a", "", None}
    assert plan_orphan_images(deleted, set()) == {"a"}
