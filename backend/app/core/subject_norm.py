"""科目/年級正規化。

Canonical 科目名 = 英文小寫 key（health/english/...）。
已知別名（中文、首大寫英文）一律轉為 canonical key；
使用者自建科目查無對映時保留原字串。
前端顯示走 i18n；後端僅在 prompt 等處需要中文時用 SUBJECT_DISPLAY_ZH。
"""

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

# 年級值域；'ALL' 表示全年級通用教材（過濾任一年級時皆命中）
VALID_GRADES = {"G1", "G2", "G3", "G4", "G5", "G6", "ALL"}

GRADE_WILDCARD = "ALL"


def normalize_subject(value):
    """已知科目別名 → canonical key；未知值 strip 後原樣返回。"""
    if value is None:
        return value
    stripped = str(value).strip()
    return SUBJECT_CANONICAL_MAP.get(stripped, stripped)


def display_subject_zh(key):
    """canonical key 的中文顯示名；未知 key 原樣返回。"""
    return SUBJECT_DISPLAY_ZH.get(key, key)


def normalize_grade(value):
    """年級收斂為 G1–G6 / ALL（大小寫不敏感）；空值與非法值歸 ''。"""
    if value is None:
        return ""
    candidate = str(value).strip().upper()
    return candidate if candidate in VALID_GRADES else ""
