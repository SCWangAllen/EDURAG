"""科目/年級正規化。

Canonical 科目名 = 英文小寫 key（health/english/...）。
已知別名（中文、首大寫英文）一律轉為 canonical key；
使用者自建科目查無對映時保留原字串。
前端顯示走 i18n；後端僅在 prompt 等處需要中文時用 SUBJECT_DISPLAY_ZH。

年級：全校分三個班別（band），此模組是「代碼 → 顯示名稱」的唯一權威來源：
  - ESL 班：K1, K2, A1, A2
  - 年級班（Grade Level）：G1–G6
  - 國中班（Junior Class，借用 G4–G6 教材）：JR4–JR9
  - ALL：通用（全年級適用），排序恆置最後
"""

import logging
import re

logger = logging.getLogger(__name__)

# 舊值（中文 / 首大寫 / 全大寫）→ canonical key
SUBJECT_CANONICAL_MAP = {
    "健康": "health",
    "Health": "health",
    "HEALTH": "health",
    "英文": "english",
    "English": "english",
    "ENGLISH": "english",
    "歷史": "history",
    "History": "history",
    "HISTORY": "history",
    "數學": "math",
    "Math": "math",
    "MATH": "math",
    "自然": "science",
    "Science": "science",
    "SCIENCE": "science",
    "國文": "chinese",
    "Chinese": "chinese",
    "CHINESE": "chinese",
    "社會": "social",
    "Social": "social",
    "SOCIAL": "social",
}

# canonical key → 中文顯示名（LLM prompt 與後端 fallback 顯示用）
SUBJECT_DISPLAY_ZH = {
    "health": "健康",
    "english": "英文",
    "history": "歷史",
    "math": "數學",
    "science": "自然",
    "chinese": "國文",
    "social": "社會",
}


def normalize_subject(value):
    """已知科目別名 → canonical key；未知值 strip 後原樣返回。"""
    if value is None:
        return value
    stripped = str(value).strip()
    return SUBJECT_CANONICAL_MAP.get(stripped, stripped)


def display_subject_zh(key):
    """canonical key 的中文顯示名；未知 key 原樣返回。"""
    return SUBJECT_DISPLAY_ZH.get(key, key)


# ---------------------------------------------------------------------------
# 年級（grade）：唯一權威來源
# ---------------------------------------------------------------------------

GRADE_WILDCARD = "ALL"
_ALL_LABEL_ZH = "通用（全年級適用）"

# 每個 band：key（內部識別）、label_zh/label_en（顯示用）、grades（(code, label) 依顯示順序）。
# 這份清單的順序即為「唯一權威」的排序依據：VALID_GRADES / GRADE_LABELS / grade_sort_key
# 皆由此衍生，不另外維護第二份清單。
GRADE_GROUPS = [
    {
        "key": "esl",
        "label_zh": "ESL 班",
        "label_en": "ESL",
        "grades": [
            ("K1", "K1"),
            ("K2", "K2"),
            ("A1", "A1"),
            ("A2", "A2"),
        ],
    },
    {
        # 注意：key 是 "grade"（不是 "grade_level"）——前端 mirror 常數用 esl/grade/junior
        # 三個 key，兩邊必須一致，否則前端依 key 對應 band 會找不到這一組。
        "key": "grade",
        "label_zh": "年級班",
        "label_en": "Grade Level",
        "grades": [
            ("G1", "G1"),
            ("G2", "G2"),
            ("G3", "G3"),
            ("G4", "G4"),
            ("G5", "G5"),
            ("G6", "G6"),
        ],
    },
    {
        "key": "junior",
        "label_zh": "國中班",
        "label_en": "Junior Class",
        "grades": [
            ("JR4", "Jr. G4"),
            ("JR5", "Jr. G5"),
            ("JR6", "Jr. G6"),
            ("JR7", "Jr. G7"),
            ("JR8", "Jr. G8"),
            ("JR9", "Jr. G9"),
        ],
    },
]

# 已知（非 ALL）年級代碼，依 band → band 內順序排列
_KNOWN_GRADE_CODES = tuple(
    code for group in GRADE_GROUPS for code, _ in group["grades"]
)

# 值域（有序）；ALL 恆置最後
VALID_GRADES = _KNOWN_GRADE_CODES + (GRADE_WILDCARD,)

# 代碼 → 顯示名稱
GRADE_LABELS = {
    code: label for group in GRADE_GROUPS for code, label in group["grades"]
}
GRADE_LABELS[GRADE_WILDCARD] = _ALL_LABEL_ZH

# 代碼 → 排序索引（0-based，依 VALID_GRADES 順序；ALL 為最大值＝最後）。
# 供 grade_sort_key() 與各 service 建構 SQL CASE 排序時共用同一份 mapping，避免漂移。
GRADE_SORT_INDEX = {code: idx for idx, code in enumerate(VALID_GRADES)}

# 輸入別名 → 代碼（去空白/句點、大寫化後比對）；用於 normalize_grade 收斂 "Jr. G4" 等寫法
_GRADE_ALIASES = {
    "全年級": GRADE_WILDCARD,
    "全年级": GRADE_WILDCARD,
}


def normalize_grade(value):
    """年級輸入 → 代碼（大小寫不敏感，忽略空白與句點）；空值與非法值歸 ''（並記錄 warning log）。

    支援的輸入形式（不分大小寫、可含空白/句點）：
      - 代碼本身：G4、K1、JR4、ALL
      - Junior 班常見別名：'Jr. G4'、'Jr.G4'、'JR G4'、'Junior Grade 4'、'Junior G4' → 'JR4'
      - 'all' / '全年級' → 'ALL'
    """
    if value is None:
        return ""
    raw = str(value).strip()
    if not raw:
        return ""

    if raw in _GRADE_ALIASES:
        return _GRADE_ALIASES[raw]

    # 去除空白與句點、大寫化：'Jr. G4' / 'Jr.G4' / 'JR G4' 皆收斂為 'JRG4'
    candidate = raw.replace(" ", "").replace(".", "").upper()

    if candidate == GRADE_WILDCARD:
        return GRADE_WILDCARD

    # 'JRG4' → 'JR4'（Junior 班常見的 'Jr. G4' 系列寫法）
    if candidate.startswith("JRG") and candidate[3:].isdigit():
        candidate = "JR" + candidate[3:]

    # 'Junior Grade 6' / 'Junior G6' / 'Junior 6'（線上舊資料的寫法）→ 'JR6'
    junior = re.fullmatch(r"JUNIOR(?:GRADE|G)?(\d)", candidate)
    if junior:
        candidate = "JR" + junior.group(1)

    if candidate in VALID_GRADES:
        return candidate

    logger.warning("normalize_grade: 無法辨識的年級值，已歸空字串: %r", value)
    return ""


def grade_sort_key(code) -> int:
    """年級代碼 → 排序索引：已知代碼依 canonical 順序（ALL 是已知代碼中的最後一個）；
    None／空字串／未知代碼一律回傳 len(VALID_GRADES)，排在所有已知代碼（含 ALL）之後。
    """
    if not code:
        return len(VALID_GRADES)
    candidate = str(code).strip().upper()
    return GRADE_SORT_INDEX.get(candidate, len(VALID_GRADES))


def grade_groups_payload() -> dict:
    """GET /api/subjects/grades 的回應內容（純函式，供 router 與測試共用）。"""
    return {
        "groups": [
            {
                "key": group["key"],
                "label": group["label_en"],
                "grades": [
                    {"code": code, "label": label} for code, label in group["grades"]
                ],
            }
            for group in GRADE_GROUPS
        ],
        "all": {"code": GRADE_WILDCARD, "label": _ALL_LABEL_ZH},
    }
