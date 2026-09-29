"""圖片名稱正規化。

Excel 匯入（image_question_service.parse_excel）只對欄位值做 `.strip()`，
但圖片上傳端點（routers/images.py 的 upload_image）用
`re.sub(r'[^a-zA-Z0-9_\\-]', '_', name)` 清理檔名、且不接受副檔名。兩邊規則
不一致，導致 Excel 填的名稱（例如 `image02.1`、`image01.png`）與實際存檔
（`image02_1`、`image01_png`）對不上，題目因此被判定「圖片缺失」。

此模組把「使用者/Excel 填的名稱」正規化成「與上傳端點相同規則」會產出的
名稱，供 Excel 匯入解析、Pydantic schema、圖片存在性檢查、以及圖片存取端點
的救援 fallback 共用同一套規則。刻意不改上傳端點本身的清理邏輯。
"""
import re

# 與 routers/images.py 的 upload_image() 字元清理規則完全一致，勿各自維護一份
_SANITIZE_PATTERN = re.compile(r"[^a-zA-Z0-9_\-]")
# 只在字串「結尾」去掉一個常見圖片副檔名（大小寫不分），最多去一次，
# 避免誤删檔名中間本來就有的點（例如 "a.b.c" 這種非副檔名用途的點）
_TRAILING_EXT_PATTERN = re.compile(r"\.(jpg|jpeg|png|webp|gif)$", re.IGNORECASE)


def normalize_image_name(name: str | None) -> str:
    """把圖片名稱正規化成與圖片上傳端點相同規則產出的檔名（不含副檔名）。

    規則：去頭尾空白 → 去掉最多一個結尾副檔名（jpg/jpeg/png/webp/gif，不分
    大小寫）→ 套用上傳端點的字元清理規則（非英數字/底線/連字號一律換成底線）。

    None 或空字串（含全空白）回傳 ""。
    """
    if not name:
        return ""
    stripped = name.strip()
    if not stripped:
        return ""
    without_ext = _TRAILING_EXT_PATTERN.sub("", stripped)
    return _SANITIZE_PATTERN.sub("_", without_ext)
