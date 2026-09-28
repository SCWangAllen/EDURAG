from app.core.subject_norm import (
    VALID_GRADES,
    display_subject_zh,
    grade_groups_payload,
    grade_sort_key,
    normalize_grade,
    normalize_subject,
)


class TestNormalizeSubject:
    def test_chinese_aliases_map_to_canonical(self):
        assert normalize_subject("健康") == "health"
        assert normalize_subject("英文") == "english"
        assert normalize_subject("歷史") == "history"
        assert normalize_subject("數學") == "math"
        assert normalize_subject("自然") == "science"
        assert normalize_subject("國文") == "chinese"
        assert normalize_subject("社會") == "social"

    def test_capitalized_english_maps_to_canonical(self):
        assert normalize_subject("Health") == "health"
        assert normalize_subject("English") == "english"
        assert normalize_subject("HISTORY") == "history"

    def test_canonical_key_is_stable(self):
        assert normalize_subject("health") == "health"

    def test_unknown_subject_kept_as_is(self):
        assert normalize_subject("地理") == "地理"

    def test_strips_whitespace(self):
        assert normalize_subject("  健康  ") == "health"

    def test_none_passthrough(self):
        assert normalize_subject(None) is None


class TestDisplaySubjectZh:
    def test_known_key(self):
        assert display_subject_zh("health") == "健康"

    def test_unknown_key_returns_raw(self):
        assert display_subject_zh("地理") == "地理"


class TestNormalizeGrade:
    def test_valid_grades_pass(self):
        for g in VALID_GRADES:
            assert normalize_grade(g) == g

    def test_case_insensitive(self):
        assert normalize_grade("g4") == "G4"
        assert normalize_grade("all") == "ALL"
        assert normalize_grade("k1") == "K1"

    def test_legacy_junior_grade_wording(self):
        # 線上舊資料的國中班寫法
        assert normalize_grade("Junior Grade 6") == "JR6"
        assert normalize_grade("junior g7") == "JR7"
        assert normalize_grade("Junior 9") == "JR9"
        assert normalize_grade("Junior Grade 10") == ""

    def test_strips_whitespace(self):
        assert normalize_grade(" G1 ") == "G1"

    def test_invalid_becomes_empty(self):
        assert normalize_grade("Grade 4") == ""
        assert normalize_grade("七年級") == ""

    def test_none_and_empty_become_empty(self):
        assert normalize_grade(None) == ""
        assert normalize_grade("") == ""

    def test_esl_grade_codes(self):
        assert normalize_grade("k1") == "K1"
        assert normalize_grade("K2") == "K2"
        assert normalize_grade("a1") == "A1"
        assert normalize_grade("A2") == "A2"

    def test_junior_grade_variants_collapse_to_canonical_code(self):
        for variant in ["Jr. G4", "Jr.G4", "JR G4", "jr4", "JR4"]:
            assert normalize_grade(variant) == "JR4"

    def test_all_variants(self):
        assert normalize_grade("all") == "ALL"
        assert normalize_grade("全年級") == "ALL"


class TestGradeSortKey:
    def test_orders_esl_before_grade_level_before_junior_before_all(self):
        assert grade_sort_key("K1") < grade_sort_key("G1")
        assert grade_sort_key("G1") < grade_sort_key("JR4")
        assert grade_sort_key("JR4") < grade_sort_key("ALL")

    def test_within_band_order_is_preserved(self):
        assert grade_sort_key("G1") < grade_sort_key("G6")
        assert grade_sort_key("JR4") < grade_sort_key("JR9")

    def test_unknown_and_empty_sort_after_all_known_codes(self):
        assert grade_sort_key("bogus") >= grade_sort_key("ALL")
        assert grade_sort_key(None) >= grade_sort_key("ALL")
        assert grade_sort_key("") >= grade_sort_key("ALL")


class TestGradeGroupsPayload:
    """GET /api/subjects/grades 的內容契約：前端 mirror 常數用 esl/grade/junior
    三個 group key，兩邊必須逐字一致，否則前端依 key 對應 band 會找不到那一組。"""

    def test_group_keys_match_frontend_mirror_contract(self):
        payload = grade_groups_payload()
        assert [g["key"] for g in payload["groups"]] == ["esl", "grade", "junior"]

    def test_all_entry_present_with_wildcard_code(self):
        payload = grade_groups_payload()
        assert payload["all"]["code"] == "ALL"

    def test_grade_band_contains_g1_through_g6(self):
        payload = grade_groups_payload()
        grade_band = next(g for g in payload["groups"] if g["key"] == "grade")
        assert [item["code"] for item in grade_band["grades"]] == [
            "G1",
            "G2",
            "G3",
            "G4",
            "G5",
            "G6",
        ]
