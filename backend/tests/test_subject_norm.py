from app.core.subject_norm import (
    display_subject_zh,
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
        for g in ["G1", "G2", "G3", "G4", "G5", "G6", "ALL"]:
            assert normalize_grade(g) == g

    def test_case_insensitive(self):
        assert normalize_grade("g4") == "G4"
        assert normalize_grade("all") == "ALL"

    def test_strips_whitespace(self):
        assert normalize_grade(" G1 ") == "G1"

    def test_invalid_becomes_empty(self):
        assert normalize_grade("Grade 4") == ""
        assert normalize_grade("七年級") == ""

    def test_none_and_empty_become_empty(self):
        assert normalize_grade(None) == ""
        assert normalize_grade("") == ""
