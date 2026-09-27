from app.core.subject_colors import (
    DEFAULT_SUBJECT_COLOR,
    SUBJECT_COLOR_PALETTE,
    assign_colors,
    is_unassigned_color,
    pick_subject_color,
)


def test_unassigned_detection():
    assert (
        is_unassigned_color(None)
        and is_unassigned_color("")
        and is_unassigned_color("#3b82f6")
    )
    assert not is_unassigned_color("#16A34A")


def test_pick_least_used_then_round_robin():
    assert pick_subject_color([]) == SUBJECT_COLOR_PALETTE[0]
    assert pick_subject_color([SUBJECT_COLOR_PALETTE[0]]) == SUBJECT_COLOR_PALETTE[1]
    # 預設藍不算「已使用」
    assert pick_subject_color([DEFAULT_SUBJECT_COLOR]) == SUBJECT_COLOR_PALETTE[0]
    # 全部用過一輪後,再從頭輪
    assert pick_subject_color(list(SUBJECT_COLOR_PALETTE)) == SUBJECT_COLOR_PALETTE[0]


def test_assign_colors_keeps_custom_and_spreads_defaults():
    existing = {
        "health": DEFAULT_SUBJECT_COLOR,
        "science": "#d8f73b",
        "english": None,
        "math": DEFAULT_SUBJECT_COLOR,
    }
    out = assign_colors(["health", "science", "english", "math"], existing)
    assert out["science"] == "#d8f73b"
    assigned = [out["health"], out["english"], out["math"]]
    assert len(set(assigned)) == 3 and all(c in SUBJECT_COLOR_PALETTE for c in assigned)
