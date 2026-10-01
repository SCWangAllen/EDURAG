from app.core.question_sanitize import (
    BLANK,
    normalize_cloze_prompt,
    normalize_matching_answer,
    strip_html,
)
from app.core.question_types import build_format_instruction


# ---- strip_html ---------------------------------------------------------
def test_strip_html_removes_inline_tags_and_entities():
    assert strip_html("The <u>heart</u> has <b>four</b> chambers.") == "The heart has four chambers."
    assert strip_html("A &amp; B&nbsp;C") == "A & B C"
    assert strip_html("The &lt;u&gt;heart&lt;/u&gt; beats.") == "The heart beats."


def test_strip_html_recurses_and_keeps_math():
    q = {"prompt": "Is 5<6?", "options": ["<i>a</i>. yes", "b. no"], "n": 3}
    assert strip_html(q) == {"prompt": "Is 5<6?", "options": ["a. yes", "b. no"], "n": 3}


# ---- cloze --------------------------------------------------------------
def test_cloze_keeps_existing_blank():
    assert normalize_cloze_prompt("The ______ pumps blood.", "heart") == "The ______ pumps blood."


def test_cloze_normalizes_alternative_markers():
    assert normalize_cloze_prompt("The ＿＿＿ pumps blood.", "heart") == f"The {BLANK} pumps blood."
    assert normalize_cloze_prompt("The [blank] pumps blood.", "heart") == f"The {BLANK} pumps blood."
    assert normalize_cloze_prompt("The __ pumps blood.", "heart") == f"The {BLANK} pumps blood."


def test_cloze_replaces_embedded_answer_case_insensitive():
    out = normalize_cloze_prompt("White blood cells fight infection.", "white blood cells")
    assert out == f"{BLANK} fight infection."


def test_cloze_multiple_answers_each_get_a_blank():
    out = normalize_cloze_prompt("The heart pumps blood and the lungs take in air.", ["heart", "lungs"])
    assert out == f"The {BLANK} pumps blood and the {BLANK} take in air."


def test_cloze_answer_must_match_whole_word():
    # "art" 是 "heart" 的子字串,不能挖成空格
    assert normalize_cloze_prompt("The heart pumps blood.", "art") is None


# ---- matching -----------------------------------------------------------
LEFT = ["Viral infection", "Bacterial infection", "Fever"]
RIGHT = ["Treated with antibiotics", "Your body works hard to cure itself", "Body temperature above normal"]


def test_matching_text_pairs_with_commas_inside_items():
    ans = ("Viral infection-Your body works hard to cure itself, "
           "Bacterial infection-Treated with antibiotics, Fever-Body temperature above normal")
    assert normalize_matching_answer(ans, LEFT, RIGHT) == "1-b, 2-a, 3-c"


def test_matching_text_pairs_matches_form_and_reversed_order():
    ans = ("Treated with antibiotics matches 'Bacterial infection'; "
           "Your body works hard to cure itself matches 'Viral infection'; "
           "Body temperature above normal matches 'Fever'")
    assert normalize_matching_answer(ans, LEFT, RIGHT) == "1-b, 2-a, 3-c"


def test_matching_index_forms():
    assert normalize_matching_answer("1-b, 2-a, 3-c", LEFT, RIGHT) == "1-b, 2-a, 3-c"
    assert normalize_matching_answer("B-1, A-2, C-3", LEFT, RIGHT) == "1-b, 2-a, 3-c"
    assert normalize_matching_answer("1-1, 2-2, 3-3", LEFT, RIGHT) == "1-a, 2-b, 3-c"


def test_matching_dict_and_list_answers():
    assert normalize_matching_answer({"Fever": "Body temperature above normal",
                                      "Viral infection": "Your body works hard to cure itself",
                                      "Bacterial infection": "Treated with antibiotics"}, LEFT, RIGHT) == "1-b, 2-a, 3-c"
    assert normalize_matching_answer([["Fever", "Body temperature above normal"]], LEFT, RIGHT) is None


def test_matching_unresolvable_returns_none():
    assert normalize_matching_answer("see explanation", LEFT, RIGHT) is None
    assert normalize_matching_answer("", LEFT, RIGHT) is None


# ---- format instruction -------------------------------------------------
def test_format_instruction_cloze_and_matching_rules():
    cloze = build_format_instruction("cloze")
    assert "______" in cloze and "Rules:" in cloze
    matching = build_format_instruction("matching", matching_pairs=10)
    assert "exactly 10" in matching
    assert "HTML" in build_format_instruction("true_false")
    assert build_format_instruction("nope") is None


def test_format_instruction_cloze_blanks_and_enumeration_items():
    cloze = build_format_instruction("cloze", cloze_blanks=2)
    assert "exactly 2 blank" in cloze and "______" in cloze
    enumeration = build_format_instruction("enumeration", enumeration_items=3)
    assert "exactly 3 items" in enumeration
    # 未指定時不注入單位數規則,保持原本不限制的行為
    assert "blank(s)" not in build_format_instruction("cloze")
    assert "must ask for exactly" not in build_format_instruction("enumeration")
    # 單位數參數只對自己的題型生效,不會互相污染
    assert "blank(s)" not in build_format_instruction("enumeration", cloze_blanks=2)
