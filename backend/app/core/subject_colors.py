"""科目顏色:新科目自動從調色盤分配,避免全部都是預設藍色而看不出差別。

顏色以「科目名稱」為單位(同一科目所有年級同色)。老師在科目管理仍可手動改。
"""

from collections import Counter
from collections.abc import Iterable

DEFAULT_SUBJECT_COLOR = "#3B82F6"  # 舊預設藍;視為「尚未指定」

# 12 色,彼此可辨、配白字或深字都讀得清楚(getTextColor 依亮度決定字色)
SUBJECT_COLOR_PALETTE: tuple[str, ...] = (
    "#2563EB",  # blue
    "#16A34A",  # green
    "#DC2626",  # red
    "#D97706",  # amber
    "#7C3AED",  # violet
    "#0891B2",  # cyan
    "#DB2777",  # pink
    "#4D7C0F",  # olive
    "#EA580C",  # orange
    "#0F766E",  # teal
    "#9333EA",  # purple
    "#B45309",  # brown
)


def is_unassigned_color(color: str | None) -> bool:
    return not color or color.strip().upper() == DEFAULT_SUBJECT_COLOR


def pick_subject_color(used_colors: Iterable[str | None]) -> str:
    """從調色盤挑「目前最少科目在用」的顏色;全部用過就從頭輪,平均分配。"""
    counts = Counter(
        c.strip().upper() for c in used_colors if c and not is_unassigned_color(c)
    )
    return min(
        SUBJECT_COLOR_PALETTE,
        key=lambda c: (counts.get(c.upper(), 0), SUBJECT_COLOR_PALETTE.index(c)),
    )


def assign_colors(
    subject_names: Iterable[str], existing: dict[str, str | None]
) -> dict[str, str]:
    """為一批科目名稱分配顏色(純函式,供腳本與測試):
    existing = {name: 目前顏色};已有非預設色的沿用,其餘依序挑最少用的色。回傳 {name: color}。"""
    result: dict[str, str] = {}
    used: list[str] = [c for c in existing.values() if c and not is_unassigned_color(c)]
    for name in subject_names:
        current = existing.get(name)
        if current and not is_unassigned_color(current):
            result[name] = current
            continue
        color = pick_subject_color(used)
        result[name] = color
        used.append(color)
    return result
