"""題目格式檢核:生成後(llm_client)與存檔前(questions router / service)共用同一套規則。

純函式、不依賴 config / DB,可直接單元測試。規則以「結構」為主:
空格、選項、答案對得上項目;內容好不好仍要老師看。
"""

import logging
import re
from collections import Counter
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, Optional

from app.core.question_sanitize import (
    BLANK,
    answer_as_list,
    answer_leaks_in_prompt,
    normalize_cloze,
    normalize_cloze_prompt,
    normalize_matching_answer,
    strip_html,
)

logger = logging.getLogger(__name__)

MAX_REFILL_ROUNDS = 2


class QuestionValidationError(ValueError):
    """存檔前檢核不過;router 轉成 422 並把訊息放在 detail(前端 Toast 直接顯示)。"""


# ---------------------------------------------------------------- 選擇題答案
_LABEL_PREFIX_RE = re.compile(r"^[A-Za-z][.)\]]\s*")


def resolve_choice_answer(answer: Any, options: Any) -> Optional[str]:
    """把選擇題答案統一成大寫字母(A、B…);答案對不到任何選項回 None。

    接受:字母("B"、"b"、"B.")、1 起算數字("2")、0 起算索引("0")、
    選項全文("B. Lung" 或 "Lung")。
    """
    if not isinstance(options, list) or len(options) < 2:
        return None
    if isinstance(answer, list):
        answer = answer[0] if answer else ""
    raw = str(answer or "").strip()
    if not raw:
        return None
    letter = re.fullmatch(r"([A-Za-z])[.)]?", raw)
    if letter:
        idx = ord(letter.group(1).upper()) - ord("A")
        return chr(ord("A") + idx) if 0 <= idx < len(options) else None
    if re.fullmatch(r"\d+", raw):
        n = int(raw)
        if 1 <= n <= len(options):
            return chr(ord("A") + n - 1)
        return "A" if n == 0 else None
    lowered = raw.lower()
    stripped = _LABEL_PREFIX_RE.sub("", raw).strip().lower()
    for i, option in enumerate(options):
        full = str(option).strip().lower()
        content = _LABEL_PREFIX_RE.sub("", str(option)).strip().lower()
        if lowered in (full, content) or stripped == content:
            return chr(ord("A") + i)
    return None


# ---------------------------------------------------------------- 單題檢核
def check_question(
    q: dict[str, Any], question_type: str, *, expected_pairs: Optional[int] = None
) -> Optional[str]:
    """依題型檢核並就地正規化一題;回傳不合格原因(中文),合格回 None。

    正規化內容:選擇題答案 → 字母;配合題答案 → "1-b, 2-c";填充題題幹 → 含 ______。
    """
    if question_type == "true_false":
        tf = str(q.get("answer", "")).strip().lower()
        tf = {"t": "true", "f": "false"}.get(tf, tf)
        if tf not in ("true", "false"):
            return "是非題答案不是 true/false"
        q["answer"] = tf

    elif question_type == "matching":
        qd = q.get("question_data")
        if not qd:
            left_top, right_top = q.get("left_items"), q.get("right_items")
            if (
                isinstance(left_top, list)
                and isinstance(right_top, list)
                and left_top
                and right_top
            ):
                qd = {"left_items": left_top, "right_items": right_top}
                q["question_data"] = qd
            else:
                return "配合題缺少 question_data(left_items / right_items)"
        if not isinstance(qd, dict):
            return "配合題 question_data 格式不正確"
        left, right = qd.get("left_items"), qd.get("right_items")
        if (
            not isinstance(left, list)
            or not isinstance(right, list)
            or not left
            or not right
        ):
            return "配合題 left_items / right_items 不是非空陣列"
        if len(left) != len(right):
            return f"配合題左右項目數不一致({len(left)} vs {len(right)})"
        normalized = normalize_matching_answer(q.get("answer"), left, right)
        if not normalized:
            return "配合題答案無法對應到左右項目"
        q["answer"] = normalized
        # 組數與老師要求不符:退回重生成(以前只記 log 就照收,老師設 10 組常拿到 5 組)。
        # 放在答案正規化之後,讓 validate_questions 能把這題留作最後的備援。
        if expected_pairs and len(left) != expected_pairs:
            return pair_mismatch_reason(len(left), expected_pairs)

    elif question_type == "single_choice":
        opts = q.get("options")
        if not isinstance(opts, list) or len(opts) < 2:
            return "選擇題選項少於 2 個"
        letter = resolve_choice_answer(q.get("answer"), opts)
        if not letter:
            return "選擇題答案不在選項中"
        q["answer"] = letter

    elif question_type == "cloze":
        had_blank = normalize_cloze_prompt(q.get("prompt"), None) is not None
        fixed = normalize_cloze(q.get("prompt"), q.get("answer"))
        if not fixed:
            return "填充題沒有空格且答案不在題幹裡"
        prompt, answer = fixed
        # 答案還留在句子裡 = 把答案寫在題目上。英文答案有字界可靠判斷,一律查;
        # 中文沒有字界(「水」出現在「需要水和陽光」很正常),只查靠答案挖出空格的題
        english = any(re.search(r"[A-Za-z]", str(a)) for a in answer_as_list(answer))
        if (english or not had_blank) and answer_leaks_in_prompt(prompt, answer):
            return "填充題答案仍出現在題幹裡"
        q["prompt"], q["answer"] = prompt, answer

    elif question_type == "sequence":
        items = q.get("items")
        if not isinstance(items, list) or not items:
            return "排序題缺少 items 陣列"
        if not isinstance(q.get("answer"), list) or not q.get("answer"):
            return "排序題答案不是陣列"
        qd = q.get("question_data")
        if not isinstance(qd, dict):
            qd = {}
        qd.setdefault("items", items)
        q["question_data"] = qd

    elif question_type == "enumeration":
        if not isinstance(q.get("answer"), list) or not q.get("answer"):
            return "列舉題答案不是陣列"

    elif question_type == "symbol_identification":
        symbols = q.get("symbols")
        if not isinstance(symbols, list) or not symbols:
            return "符號題缺少 symbols 陣列"

    return None


def _prompt_key(prompt: Any) -> str:
    return re.sub(r"[^a-z0-9一-鿿]+", "", str(prompt or "").lower())


def dedupe_questions(questions: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """題幹(去大小寫與標點)相同者只留第一題。"""
    seen: set[str] = set()
    kept: list[dict[str, Any]] = []
    for q in questions:
        key = _prompt_key(q.get("prompt"))
        if key and key in seen:
            continue
        seen.add(key)
        kept.append(q)
    return kept


PAIR_MISMATCH_PREFIX = "配合題組數"


def pair_mismatch_reason(actual: int, expected: int) -> str:
    return f"{PAIR_MISMATCH_PREFIX} {actual} 與要求 {expected} 不符"


def matching_pair_count(q: dict[str, Any]) -> int:
    return len((q.get("question_data") or {}).get("left_items") or [])


def validate_questions(
    questions: Sequence[dict[str, Any]],
    question_type: str,
    *,
    expected_pairs: Optional[int] = None,
    pair_mismatch_out: Optional[list[dict[str, Any]]] = None,
) -> tuple[list[dict[str, Any]], Counter]:
    """模型輸出 → (合格且已正規化的題目, 丟棄原因計數)。

    pair_mismatch_out:給了就把「只因配對組數不符而退回」的題目收進去(其餘檢核都過、
    答案已正規化),補生成用完仍不足時可由 top_up_with_pair_mismatches 拿來備援。
    """
    validated: list[dict[str, Any]] = []
    reasons: Counter = Counter()
    for raw in questions:
        q = strip_html(raw)
        if not q.get("prompt") or not q.get("answer") or not q.get("explanation"):
            reasons["缺少 prompt / answer / explanation"] += 1
            continue
        reason = check_question(q, question_type, expected_pairs=expected_pairs)
        if reason:
            reasons[reason] += 1
            if pair_mismatch_out is not None and reason.startswith(PAIR_MISMATCH_PREFIX):
                pair_mismatch_out.append(q)
            logger.warning(
                "Dropped %s question (%s): %s",
                question_type,
                reason,
                str(q.get("prompt"))[:80],
            )
            continue
        validated.append(q)
    before = len(validated)
    validated = dedupe_questions(validated)
    if len(validated) < before:
        reasons["題幹重複"] += before - len(validated)
    logger.info(
        "Validation: %d/%d %s questions passed",
        len(validated),
        len(questions),
        question_type,
    )
    return validated, reasons


def top_up_with_pair_mismatches(
    validated: Sequence[dict[str, Any]],
    count: int,
    mismatched: Sequence[dict[str, Any]],
    expected_pairs: int,
) -> list[dict[str, Any]]:
    """補生成用完仍不足 count 時,用「只因組數不符被退回」的配合題補位:組數最接近
    要求者優先(同距離取組數多的),每題掛上 warnings 讓前端標示,老師自行決定去留。
    已合格的題目順序與內容不動。"""
    kept = list(validated)
    if len(kept) >= count or not mismatched:
        return kept
    ranked = sorted(
        mismatched,
        key=lambda q: (abs(matching_pair_count(q) - expected_pairs), -matching_pair_count(q)),
    )
    merged = dedupe_questions([*kept, *ranked])[:count]
    for q in merged[len(kept):]:
        q["warnings"] = [
            {
                "code": "matching_pairs",
                "actual": matching_pair_count(q),
                "expected": expected_pairs,
            }
        ]
    return merged


RequestMore = Callable[[int, list[str]], Awaitable[Sequence[dict[str, Any]]]]


async def refill_questions(
    validated: Sequence[dict[str, Any]],
    count: int,
    request_more: RequestMore,
    *,
    max_rounds: int = MAX_REFILL_ROUNDS,
) -> tuple[list[dict[str, Any]], int]:
    """題數不足就再要:request_more(缺的題數, 已有題幹) 回傳「已檢核」的新題,
    去重後湊滿 count 或用完 max_rounds 為止。回傳 (題目, 實際補的輪數)。"""
    kept = dedupe_questions(validated)
    rounds = 0
    while len(kept) < count and rounds < max_rounds:
        rounds += 1
        shortfall = count - len(kept)
        more = await request_more(shortfall, [str(q.get("prompt", "")) for q in kept])
        kept = dedupe_questions([*kept, *more])
        logger.info("Refill round %d: +%d → %d/%d", rounds, len(more), len(kept), count)
    return kept[:count], rounds


# ---------------------------------------------------------------- 存檔前檢核
# 存檔形式(questions 表)與生成形式不同:陣列答案存成 JSON 字串、排序項目在
# question_data.items、符號題沒有 symbols 欄位。只檢核存檔形式對得上的題型。
SAVE_CHECKED_TYPES = frozenset(
    {"single_choice", "true_false", "cloze", "matching", "sequence", "enumeration"}
)


def normalize_question_payload(
    question_type: Optional[str],
    content: Optional[str],
    options: Any,
    answer: Any,
    question_data: Any,
) -> tuple[dict[str, Any], list[str]]:
    """存檔 / 更新前用同一套規則檢核;回傳 (正規化後的欄位, 問題清單)。
    欄位:content、answer、options、question_data;問題清單為空即合格。"""
    q: dict[str, Any] = {
        "prompt": strip_html(content or ""),
        "answer": strip_html(answer),
        "options": strip_html(options),
        "question_data": strip_html(question_data),
    }
    problems: list[str] = []
    if not str(q["prompt"]).strip():
        problems.append("題幹不可為空")
    if q["answer"] is None or (
        isinstance(q["answer"], str) and not q["answer"].strip()
    ):
        problems.append("答案不可為空")
    if not problems and question_type in SAVE_CHECKED_TYPES:
        if question_type in ("sequence", "enumeration"):
            q["answer"] = answer_as_list(q["answer"])
        if question_type == "sequence" and isinstance(q["question_data"], dict):
            q["items"] = q["question_data"].get("items")
        reason = check_question(q, question_type)
        if reason:
            problems.append(reason)
    return (
        {
            "content": q["prompt"],
            "answer": q["answer"],
            "options": q["options"],
            "question_data": q["question_data"],
        },
        problems,
    )


__all__ = [
    "BLANK",
    "MAX_REFILL_ROUNDS",
    "QuestionValidationError",
    "check_question",
    "dedupe_questions",
    "normalize_question_payload",
    "refill_questions",
    "resolve_choice_answer",
    "validate_questions",
]
