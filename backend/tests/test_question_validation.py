import pytest

from app.core.question_sanitize import normalize_cloze, normalize_cloze_prompt
from app.core.question_validation import (
    check_question,
    dedupe_questions,
    normalize_question_payload,
    refill_questions,
    resolve_choice_answer,
    validate_questions,
)

OPTS = ["A. Heart", "B. Lung", "C. Liver", "D. Skin"]


# ---- 選擇題答案解析 ----------------------------------------------------
@pytest.mark.parametrize("answer,expected", [
    ("B", "B"), ("b", "B"), ("B.", "B"), ("2", "B"), ("0", "A"),
    ("B. Lung", "B"), ("Lung", "B"), ("lung", "B"), (["C"], "C"),
    ("Kidney", None), ("E", None), ("9", None), ("", None),
])
def test_resolve_choice_answer(answer, expected):
    assert resolve_choice_answer(answer, OPTS) == expected


# ---- 填充題詞形放寬 ------------------------------------------------------
def test_cloze_variants_article_plural_punctuation():
    assert normalize_cloze_prompt("The lungs take in air.", "lung") == "The ______ take in air."
    # 挖掉的是 lungs → 答案跟著改成 lungs;本來就有空格的答案不動
    assert normalize_cloze("The lungs take in air.", "lung") == ("The ______ take in air.", "lungs")
    assert normalize_cloze("The ______ take in air.", "lung") == ("The ______ take in air.", "lung")
    assert normalize_cloze("The heart and the lungs.", ["heart", "lung"]) == ("The ______ and the ______.", ["heart", "lungs"])
    assert normalize_cloze_prompt("Blood flows through the heart.", "the heart") == "Blood flows through the ______."
    assert normalize_cloze_prompt("Bees make honey.", "bee.") == "______ make honey."
    # 短變體不收:答案 "as" 不會誤挖冠詞 a
    assert normalize_cloze_prompt("A dog is as fast.", "as") == "A dog is ______ fast."


# ---- 單題檢核與正規化 ----------------------------------------------------
def test_check_question_normalizes_choice_and_rejects_bad_answer():
    q = {"prompt": "Which organ pumps blood?", "options": OPTS, "answer": "Heart"}
    assert check_question(q, "single_choice") is None and q["answer"] == "A"
    bad = {"prompt": "x", "options": OPTS, "answer": "Kidney"}
    assert check_question(bad, "single_choice") == "選擇題答案不在選項中"


def test_check_question_true_false_accepts_t_f():
    q = {"prompt": "x", "answer": "T"}
    assert check_question(q, "true_false") is None and q["answer"] == "true"
    assert check_question({"prompt": "x", "answer": "yes"}, "true_false") == "是非題答案不是 true/false"


def test_check_question_cloze_leak_and_missing_blank():
    leak = {"prompt": "The heart pumps blood; the ______ has four chambers.", "answer": "heart"}
    assert check_question(leak, "cloze") == "填充題答案仍出現在題幹裡"
    missing = {"prompt": "What organ pumps blood?", "answer": "heart"}
    assert check_question(missing, "cloze") == "填充題沒有空格且答案不在題幹裡"
    ok = {"prompt": "White blood cells fight germs.", "answer": "white blood cells"}
    assert check_question(ok, "cloze") is None and ok["prompt"].startswith("______")


def test_check_question_matching_non_dict_question_data_is_reason_not_exception():
    q = {"prompt": "p", "answer": "1-a", "question_data": "left: a; right: b"}
    assert check_question(q, "matching") == "配合題 question_data 格式不正確"


def test_cloze_leak_rule_scope():
    # 中文:模型自己留了空格,答案(水)在句子別處出現是正常句子 → 不丟
    q = {"prompt": "植物的根吸收 ______ ，葉子需要水和陽光", "answer": "水"}
    assert check_question(q, "cloze") is None
    # 中文:沒空格、靠答案挖的,答案還留在別處 → 丟
    q = {"prompt": "植物需要水，根吸收水", "answer": "水"}
    assert check_question(q, "cloze") == "填充題答案仍出現在題幹裡"
    # 沒空格、靠答案挖的,答案還留在別處 → 丟
    q = {"prompt": "The heart pumps blood and the heart has four chambers.", "answer": "heart"}
    assert check_question(q, "cloze") == "填充題答案仍出現在題幹裡"


def test_cloze_bracketed_answer_keeps_full_form():
    assert normalize_cloze("The formula is H2O (water) today.", "H2O (water)") == (
        "The formula is ______ today.", "H2O (water)")


def test_check_question_matching_requires_equal_sides_and_resolvable_answer():
    q = {"prompt": "Match.", "answer": "1-b, 2-a",
         "question_data": {"left_items": ["Fever", "Cold"], "right_items": ["Runny nose", "High temperature"]}}
    assert check_question(q, "matching", expected_pairs=10) is None
    q["question_data"]["right_items"].append("extra")
    assert check_question(q, "matching").startswith("配合題左右項目數不一致")


def test_validate_questions_collects_reasons_and_dedupes():
    qs = [
        {"prompt": "Q one?", "options": OPTS, "answer": "A", "explanation": "e"},
        {"prompt": "q one", "options": OPTS, "answer": "B", "explanation": "e"},   # 重複題幹
        {"prompt": "Q two?", "options": OPTS, "answer": "Kidney", "explanation": "e"},
        {"prompt": "Q three?", "options": OPTS, "answer": "C"},                     # 缺 explanation
    ]
    valid, reasons = validate_questions(qs, "single_choice")
    assert [q["prompt"] for q in valid] == ["Q one?"]
    assert reasons["題幹重複"] == 1
    assert reasons["選擇題答案不在選項中"] == 1
    assert reasons["缺少 prompt / answer / explanation"] == 1


def test_dedupe_keeps_first():
    assert len(dedupe_questions([{"prompt": "A b."}, {"prompt": "a B"}, {"prompt": "C"}])) == 2


# ---- 補生成迴圈 ----------------------------------------------------------
@pytest.mark.asyncio
async def test_refill_until_enough_then_stops():
    calls = []

    async def request_more(shortfall, existing):
        calls.append((shortfall, list(existing)))
        return [{"prompt": f"new {len(calls)}-{i}"} for i in range(shortfall - 1)] + [{"prompt": existing[0]}]

    got, rounds = await refill_questions([{"prompt": "seed"}], 4, request_more)
    # 第 1 輪缺 3,拿到 2 新 + 1 重複 → 3 題;第 2 輪缺 1,拿到 0 新 + 1 重複 → 仍 3 題;用完 2 輪停
    assert rounds == 2 and len(got) == 3
    assert calls[0][0] == 3 and calls[1][0] == 1 and calls[0][1] == ["seed"]


@pytest.mark.asyncio
async def test_refill_not_called_when_enough():
    async def request_more(shortfall, existing):
        raise AssertionError("should not be called")

    got, rounds = await refill_questions([{"prompt": "a"}, {"prompt": "b"}], 2, request_more)
    assert rounds == 0 and len(got) == 2


# ---- 存檔前檢核 ----------------------------------------------------------
def test_normalize_question_payload():
    fields, problems = normalize_question_payload("cloze", "The heart pumps blood.", None, "the heart.", None)
    assert problems == [] and fields["content"] == "The ______ pumps blood." and fields["answer"] == "heart"
    _, problems = normalize_question_payload("cloze", "What pumps blood?", None, "heart", None)
    assert problems == ["填充題沒有空格且答案不在題幹裡"]
    fields, problems = normalize_question_payload("single_choice", "Q?", OPTS, "B. Lung", None)
    assert problems == [] and fields["answer"] == "B"
    _, problems = normalize_question_payload("single_choice", "", OPTS, "", None)
    assert problems == ["題幹不可為空", "答案不可為空"]
    # 存檔形式:排序題項目在 question_data.items、答案是 JSON 字串;列舉題答案逗號分隔
    fields, problems = normalize_question_payload(
        "sequence", "Put in order", None, '["a", "b", "c"]', {"items": ["b", "a", "c"]})
    assert problems == [] and fields["answer"] == ["a", "b", "c"] and fields["question_data"]["items"] == ["b", "a", "c"]
    _, problems = normalize_question_payload("sequence", "Put in order", None, '["a"]', None)
    assert problems == ["排序題缺少 items 陣列"]
    fields, problems = normalize_question_payload("enumeration", "List three fruits", None, "apple, banana, cherry", None)
    assert problems == [] and fields["answer"] == ["apple", "banana", "cherry"]
    # 符號題 / 圖片題 / 未知題型:存檔形式對不上,不檢核
    for t in ("symbol_identification", "diagram_question", None, "weird"):
        assert normalize_question_payload(t, "stem", None, "ans", None)[1] == []
    # question_data 非 dict 不會炸
    _, problems = normalize_question_payload("matching", "M", None, "1-a", "not a dict")
    assert problems == ["配合題 question_data 格式不正確"]
    # 多空格填充題:前端會把陣列答案 JSON.stringify 後送來
    fields, problems = normalize_question_payload("cloze", "The heart and the lungs.", None, '["heart", "lung"]', None)
    assert problems == [] and fields["content"] == "The ______ and the ______."
    assert fields["answer"] == '["heart", "lungs"]'   # 字串進、字串出(router 直接存)
