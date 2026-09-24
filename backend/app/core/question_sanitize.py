"""生成後題目內容的正規化(純函式,不依賴 config / DB,可直接單元測試)。

- strip_html:模型偶爾在題幹/選項夾帶 <u>、<b> 等標籤,PDF 會原樣印出。
- normalize_cloze_prompt:填充題題幹一定要有 ______;模型常把答案直接寫進句子,
  或用全形底線 / [blank] 等寫法,前端只認固定幾種標記。
- normalize_matching_answer:配合題答案統一存成索引形式 "1-b, 2-c, 3-a",
  數字 = right_items(說明,試卷左欄題號)1 起算、字母 = left_items(詞語,
  試卷右欄字母);前端答案卷靠它把詞語印在底線上。
"""

import re
from collections.abc import Sequence
from typing import Any, Optional

BLANK = "______"

_TAG_RE = re.compile(
    r"</?(?:u|b|i|em|strong|br|p|span|sub|sup|mark|s|del|ins|small|div|font)"
    r"(?:\s[^<>]*)?\s*/?>",
    re.IGNORECASE,
)
_ENTITIES = {
    "&nbsp;": " ",
    "&amp;": "&",
    "&lt;": "<",
    "&gt;": ">",
    "&quot;": '"',
    "&#39;": "'",
}

# 模型可能用的各種「空格」寫法 → 統一成 ______
_ALT_BLANK_RE = re.compile(
    r"_{2,}|＿+|\[\s*(?:blank)?\s*\]|\(\s*(?:blank)?\s*\)|\{\s*(?:blank)?\s*\}"
    r"|<\s*blank\s*>|_blank_",
    re.IGNORECASE,
)

_PAIR_SEP_RE = re.compile(r"[,;，；\n]")
_TOKEN_SEP_RE = re.compile(r"\s*[-–—:=→：]\s*")


def strip_html(value: Any) -> Any:
    """遞迴去除字串中的 HTML 標籤與常見實體;非字串原樣回傳。"""
    if isinstance(value, str):
        # 先解實體再去標籤:被轉義的 &lt;u&gt; 一樣要清掉
        text = value
        for entity, plain in _ENTITIES.items():
            text = text.replace(entity, plain)
        text = _TAG_RE.sub("", text)
        return re.sub(r"[ \t]{2,}", " ", text).strip()
    if isinstance(value, list):
        return [strip_html(v) for v in value]
    if isinstance(value, dict):
        return {k: strip_html(v) for k, v in value.items()}
    return value


def normalize_cloze_prompt(prompt: str, answer: Any) -> Optional[str]:
    """回傳含 ______ 的題幹;無法補出空格時回傳 None(呼叫端應丟棄該題)。"""
    text = _ALT_BLANK_RE.sub(BLANK, str(prompt or ""))
    if BLANK in text:
        return text
    answers = answer if isinstance(answer, list) else [answer]
    for ans in answers:
        ans = str(ans or "").strip()
        if not ans:
            continue
        pattern = r"(?<![A-Za-z0-9])" + re.escape(ans) + r"(?![A-Za-z0-9])"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            text = text[: match.start()] + BLANK + text[match.end() :]
    return text if BLANK in text else None


def _index_token(token: str) -> tuple[Optional[str], int]:
    """'3' → ('num', 2);'b' → ('alpha', 1);其他 → (None, -1)。"""
    t = token.strip()
    if re.fullmatch(r"\d+", t):
        return "num", int(t) - 1
    if re.fullmatch(r"[A-Za-z]", t):
        return "alpha", ord(t.upper()) - ord("A")
    return None, -1


def _pairs_from_index_form(text: str, left_n: int, right_n: int) -> dict[int, int]:
    """解析 '1-b, 2-c' 或 'A-2' 或 '1-1':數字 → right、字母 → left;
    同型時退回「第一個 = left、第二個 = right」。回傳 {right_idx: left_idx}。"""
    mapping: dict[int, int] = {}
    for pair in _PAIR_SEP_RE.split(text):
        parts = [p for p in _TOKEN_SEP_RE.split(pair.strip()) if p]
        if len(parts) != 2:
            return {}
        (k0, i0), (k1, i1) = _index_token(parts[0]), _index_token(parts[1])
        if k0 is None or k1 is None:
            return {}
        if k0 == "num" and k1 == "alpha":
            right_i, left_i = i0, i1
        elif k0 == "alpha" and k1 == "num":
            left_i, right_i = i0, i1
        else:
            left_i, right_i = i0, i1
        if not (0 <= left_i < left_n and 0 <= right_i < right_n):
            return {}
        mapping[right_i] = left_i
    return mapping


def _pairs_from_text(
    text: str, left: Sequence[str], right: Sequence[str]
) -> dict[int, int]:
    """答案是「詞語-說明, 詞語-說明」全文時,用項目文字在答案中的出現位置配對。
    左右項目相鄰出現即為一組(順序不拘);較長的項目優先,避免子字串誤判。"""
    lowered = text.lower()
    found: list[tuple[int, int, str, int]] = []  # (start, -length, side, idx)
    for side, items in (("L", left), ("R", right)):
        for idx, item in enumerate(items):
            needle = str(item).strip().lower()
            if not needle:
                continue
            start = lowered.find(needle)
            while start != -1:
                found.append((start, -len(needle), side, idx))
                start = lowered.find(needle, start + 1)
    found.sort()
    mapping: dict[int, int] = {}
    pending: Optional[tuple[str, int]] = None
    last_end = -1
    for start, neg_len, side, idx in found:
        if start < last_end:
            continue  # 與前一個已採用的項目重疊(子字串)
        last_end = start - neg_len
        if pending and pending[0] != side:
            left_i, right_i = (idx, pending[1]) if side == "L" else (pending[1], idx)
            mapping[right_i] = left_i
            pending = None
        else:
            pending = (side, idx)
    return mapping


def normalize_matching_answer(
    answer: Any, left: Sequence[str], right: Sequence[str]
) -> Optional[str]:
    """把各種寫法的配合題答案統一成 '1-b, 2-c, 3-a';解析不出完整對應時回傳 None。"""
    if isinstance(answer, dict):
        text = "; ".join(f"{k} - {v}" for k, v in answer.items())
    elif isinstance(answer, list):
        text = "; ".join(
            " - ".join(str(x) for x in a) if isinstance(a, (list, tuple)) else str(a)
            for a in answer
        )
    else:
        text = str(answer or "")
    text = text.strip()
    if not text or not left or not right:
        return None

    mapping = _pairs_from_index_form(text, len(left), len(right))
    if len(mapping) < len(right):
        text_mapping = _pairs_from_text(text, left, right)
        if len(text_mapping) > len(mapping):
            mapping = text_mapping
    if len(mapping) < len(right):
        return None
    return ", ".join(
        f"{ri + 1}-{chr(ord('a') + mapping[ri])}" for ri in sorted(mapping)
    )
