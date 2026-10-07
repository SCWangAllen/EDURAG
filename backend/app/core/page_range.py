"""文件頁碼（documents.page_number）的區間解析與 SQL 篩選條件。

page_number 是自由格式文字（"71"、"100-101"、"p.12"、"pp. 115-171"、"xxii" 等），
教師篩選考試範圍時習慣用「頁 115-171」描述，因此需要把文字轉成可比較的
(起點, 迄點) 數字區間；轉不出數字的（例如序言常見的羅馬數字 "xxii"）視為無法篩選。

parse_page_range 是純函式，供 Excel 上傳解析標記警示與測試共用；
page_range_conditions 回傳 SQLAlchemy 條件，供 DocumentService.get_documents 套用。
"""

import re
from typing import Optional

from sqlalchemy import Numeric, cast, func

# 全形數字轉半形的位移量（'０'(U+FF10) 對應 '0'(U+0030)）
_FULLWIDTH_DIGIT_OFFSET = ord("０") - ord("0")
# 各種橫線/波浪號寫法統一轉成半形 '-'：全形減號、em dash、en dash、波浪號、全形波浪號
_DASH_RE = re.compile("[－—–～~]")
# 只在「數字.數字」時才視為小數去尾（Excel 數字格儲存成 10.0/99.0 的常見情況）；
# 用 lookbehind 限定小數點前面必須是數字，才不會吃掉像 "p.12" 這種頁碼前綴寫法
# （"p.12" 的 "." 前面是 "p"，不是數字，不會被去掉）。
_DECIMAL_SUFFIX_RE = re.compile(r"(?<=\d)\.\d+")
_DIGIT_RE = re.compile(r"\d+")

# 給 SQL 版本使用的同義正則（字串形式，直接傳給 Postgres regexp_replace/substring）
_FULLWIDTH_DIGITS = "０１２３４５６７８９"
_HALFWIDTH_DIGITS = "0123456789"
_SQL_DECIMAL_SUFFIX_PATTERN = r"(?<=\d)\.\d+"
_SQL_FIRST_NUMBER_PATTERN = r"(\d+)"
_SQL_LAST_NUMBER_PATTERN = r"(\d+)\D*$"


def _normalize(text: str) -> str:
    """全形數字轉半形、各種橫線/波浪號統一轉成 '-'。"""
    normalized = "".join(
        chr(ord(ch) - _FULLWIDTH_DIGIT_OFFSET) if "０" <= ch <= "９" else ch
        for ch in text
    )
    return _DASH_RE.sub("-", normalized)


def parse_page_range(value) -> Optional[tuple[int, int]]:
    """解析自由格式頁碼文字為 (起點, 迄點) 區間；解析不出數字時回傳 None。

    - None 或空白字串 → None
    - 全形數字、各種橫線先正規化
    - 去掉貼在數字後面的小數部分（"10.0" → "10"）
    - 取出全部數字：第一個當起點、最後一個當迄點；迄點小於起點時自動交換
    - 單一數字（例如 "71"）→ (71, 71)
    - 一個數字都取不出來（例如序言常見的羅馬數字 "xxii"）→ None

    範例："pp. 115-171" → (115, 171)；"p.12" → (12, 12)；"100-101" → (100, 101)。
    """
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    text = _normalize(text)
    text = _DECIMAL_SUFFIX_RE.sub("", text)

    numbers = _DIGIT_RE.findall(text)
    if not numbers:
        return None

    start, end = int(numbers[0]), int(numbers[-1])
    if end < start:
        start, end = end, start
    return start, end


def page_bounds(column):
    """把自由文字頁碼欄轉成 (start, end_) 兩個可比較的 SQL 數值運算式（NUMERIC）。

    與 parse_page_range 語意一致：全形數字轉半形 → 去掉貼在數字後面的小數 →
    第一個數字當 start、最後一個數字當 end_（抓不到就退回 start）。
    抓不到任何數字時 start 為 NULL。page_range_conditions 與 Alembic 回填共用。
    """
    # 全形數字先轉半形(Postgres 的 \d 不認得 "１"),與 parse_page_range 的正規化一致;
    # 轉成 NUMERIC 而非 INTEGER:頁碼欄是自由文字,11 位以上的數字串(例如 ISBN)用
    # INTEGER 會整個查詢 out of range 噴 500
    halfwidth = func.translate(column, _FULLWIDTH_DIGITS, _HALFWIDTH_DIGITS)
    cleaned = func.regexp_replace(halfwidth, _SQL_DECIMAL_SUFFIX_PATTERN, "", "g")
    start = cast(func.substring(cleaned, _SQL_FIRST_NUMBER_PATTERN), Numeric)
    end_ = func.coalesce(
        cast(func.substring(cleaned, _SQL_LAST_NUMBER_PATTERN), Numeric), start
    )
    return start, end_


def page_range_conditions(
    column, page_from: Optional[int] = None, page_to: Optional[int] = None
) -> list:
    """頁碼範圍篩選的 SQLAlchemy 條件清單（純函式，可直接編譯 SQL 做測試）。

    與 parse_page_range 語意一致，但在 SQL 端計算，供 DocumentService.get_documents
    套用在 Document.page_number 這個 TEXT 欄位上：
    - cleaned：先去掉貼在數字後面的小數部分
    - start：cleaned 裡第一個數字
    - end_：cleaned 裡最後一個數字（抓不到就 fallback 回 start，對齊「單一頁碼」語意）

    page_from / page_to 都沒給時回傳空清單（不加任何條件）。給了任一個時，
    無法解析出頁碼數字的列（例如羅馬數字 "xxii"）一律排除——否則「有篩頁碼」
    卻把無法判斷頁碼範圍的列也列進結果，教師會誤以為那些列落在篩選範圍內。
    """
    start, end_ = page_bounds(column)

    conditions: list = []
    if page_from is None and page_to is None:
        return conditions

    conditions.append(start.isnot(None))
    if page_from is not None:
        conditions.append(end_ >= page_from)
    if page_to is not None:
        conditions.append(start <= page_to)
    return conditions


def page_containment_conditions(
    from_column,
    to_column,
    page_from: Optional[int] = None,
    page_to: Optional[int] = None,
) -> list:
    """題目自己記的頁碼範圍（questions.page_from / page_to 整數欄）的篩選條件：
    「包含」語意——題目的整個範圍都要落在教師查的區間裡，兩端都比。

    與教材列表的「重疊」語意刻意不同：全選整本書生成的題目會記成 1–171，
    用重疊語意查 32–37 它也會跑出來，頁碼篩選就等於沒用；用包含語意它只有在
    教師也查很大範圍時才出現，正好符合它的用途（週考 / 複習卷）。
    只給一端時只比那一端。沒記範圍的題目（兩欄 NULL）比較結果是 NULL，自動排除。
    """
    conditions: list = []
    if page_from is not None:
        conditions.append(from_column >= page_from)
    if page_to is not None:
        conditions.append(to_column <= page_to)
    return conditions
