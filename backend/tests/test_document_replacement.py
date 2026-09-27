"""重新上傳判斷是否該取代既有文件的邏輯測試。

find_replacement_targets 是純函式（不觸 DB），比對正規化科目 + 年級（大小寫不敏感）
+ trim 後小寫的章節/標題/頁碼，用來決定 Excel 重新上傳時該 UPDATE 既有列還是 INSERT
新列。回傳 (mapping, ambiguous_indices)：key 在既有資料或本次上傳中不唯一時視為
模糊，不猜測，一律當新增並回報在 ambiguous_indices。
save_documents 的 created/replaced 契約另用假的 DocumentService 驗證（不需真的 DB）。
"""
import pytest

from app.services.document_service import chapter_sort_key, find_replacement_targets
from app.services.upload_service import save_documents


def _row(
    id_,
    subject="health",
    grade="G4",
    chapter="Chapter 4",
    title="Body Defenses",
    page_number="1",
):
    return {
        "id": id_,
        "subject": subject,
        "grade": grade,
        "chapter": chapter,
        "title": title,
        "page_number": page_number,
    }


def _doc(
    index,
    subject="health",
    grade="G4",
    chapter="Chapter 4",
    title="Body Defenses",
    page_number="1",
):
    return {
        "index": index,
        "subject": subject,
        "grade": grade,
        "chapter": chapter,
        "title": title,
        "page_number": page_number,
    }


def test_exact_match_after_normalization_is_flagged_for_replacement():
    existing = [_row(42)]
    new_docs = [
        _doc(
            1,
            subject="Health",  # 大小寫不同
            grade="g4",  # 大小寫不同
            chapter="  Chapter 4  ",  # 前後空白
            title="body defenses",  # 大小寫不同
            page_number=" 1 ",  # 前後空白
        )
    ]

    mapping, ambiguous = find_replacement_targets(existing, new_docs)

    assert mapping == {1: 42}
    assert ambiguous == set()


def test_chinese_alias_subject_matches_canonical_english_subject():
    existing = [_row(7, grade="ALL", chapter="營養教育", title="健康飲食指南", page_number=None)]
    new_docs = [
        _doc(
            1,
            subject="健康",
            grade="ALL",
            chapter="營養教育",
            title="健康飲食指南",
            page_number=None,
        )
    ]

    mapping, ambiguous = find_replacement_targets(existing, new_docs)

    assert mapping == {1: 7}
    assert ambiguous == set()


def test_no_match_when_chapter_differs():
    existing = [_row(1)]
    new_docs = [_doc(1, chapter="Chapter 5")]

    mapping, ambiguous = find_replacement_targets(existing, new_docs)

    assert mapping == {}
    assert ambiguous == set()


def test_only_matching_docs_appear_in_result():
    existing = [_row(1)]
    new_docs = [
        _doc(1),
        _doc(
            2,
            subject="history",
            chapter="New Chapter",
            title="New Title",
            page_number="9",
        ),
    ]

    mapping, ambiguous = find_replacement_targets(existing, new_docs)

    assert mapping == {1: 1}
    assert 2 not in mapping
    assert ambiguous == set()


def test_same_chapter_multiple_pages_replace_their_own_row_not_one_shared_row():
    """迴歸測試（CRITICAL）：重新上傳同一章節的 3 個 Page 列，過去因為 title 是從
    chapter 推導、三列 title 完全相同，導致全部誤判成同一筆既有文件；現在應各自
    依 page_number 對應到各自的既有列。"""
    existing = [
        _row(101, chapter="Chapter 4", title="Body Defenses", page_number="70"),
        _row(102, chapter="Chapter 4", title="Body Defenses", page_number="71"),
        _row(103, chapter="Chapter 4", title="Body Defenses", page_number="72"),
    ]
    new_docs = [
        _doc(1, chapter="Chapter 4", title="Body Defenses", page_number="70"),
        _doc(2, chapter="Chapter 4", title="Body Defenses", page_number="71"),
        _doc(3, chapter="Chapter 4", title="Body Defenses", page_number="72"),
    ]

    mapping, ambiguous = find_replacement_targets(existing, new_docs)

    assert mapping == {1: 101, 2: 102, 3: 103}
    assert ambiguous == set()
    # 三個既有 id 都各自被消耗一次，沒有任何一筆被兩個新列共用
    assert len(set(mapping.values())) == 3


def test_ambiguous_when_existing_rows_share_the_same_key():
    """既有資料本身就有兩筆完全同 key（例如過去手動誤匯入造成的重複），
    無法確定該取代哪一筆時不猜測，回報為 ambiguous 並當新增。"""
    existing = [_row(5), _row(9)]
    new_docs = [_doc(1)]

    mapping, ambiguous = find_replacement_targets(existing, new_docs)

    assert mapping == {}
    assert ambiguous == {1}


def test_ambiguous_when_new_docs_share_the_same_key():
    """本次上傳內有兩列共用同一個 key（例如頁碼也重複），
    無法確定該取代既有的那一筆時不猜測，兩列都當新增並回報 ambiguous。"""
    existing = [_row(1)]
    new_docs = [_doc(1), _doc(2)]  # 兩筆完全相同的 key（含 page_number）

    mapping, ambiguous = find_replacement_targets(existing, new_docs)

    assert mapping == {}
    assert ambiguous == {1, 2}


def test_chapter_sort_key_matches_natural_number_ordering():
    """chapter_sort_key 讓 MockDocumentService 的排序與真實 DB 的
    substring(...)::int NULLS LAST, chapter ASC 語意一致：數字小的在前、
    無數字或 None 排最後，None 排在「有文字但無數字」之後。"""
    values = ["Chapter 10", "Chapter 2", "Intro", None]

    ordered = sorted(values, key=chapter_sort_key)

    assert ordered == ["Chapter 2", "Chapter 10", "Intro", None]


class _FakeDocumentService:
    """save_documents 的假雙面：不觸真的 DB，記錄呼叫方式即可驗證 created/replaced 契約。"""

    def __init__(self, replace_ok: bool = True):
        self.replace_ok = replace_ok
        self.created_payloads = []
        self.replaced_ids = []

    async def create_document(self, payload):
        self.created_payloads.append(payload)
        return {"id": 999, **payload}

    async def replace_document(self, document_id, payload):
        if self.replace_ok:
            self.replaced_ids.append(document_id)
            return True
        return False


@pytest.mark.asyncio
async def test_save_documents_counts_created_and_replaced_separately():
    service = _FakeDocumentService(replace_ok=True)
    docs = [
        {
            "index": 1,
            "title": "New Doc",
            "content": "c",
            "subject": "health",
            "grade": "G4",
            "page_number": None,
            "chapter": "Chapter 1",
            "image_filename": None,
            "source_filename": "upload.xlsx",
            "replaces_id": None,
        },
        {
            "index": 2,
            "title": "Existing Doc",
            "content": "c2",
            "subject": "health",
            "grade": "G4",
            "page_number": None,
            "chapter": "Chapter 2",
            "image_filename": None,
            "source_filename": "upload.xlsx",
            "replaces_id": 42,
        },
    ]

    created, replaced, errors = await save_documents(docs, service)

    assert created == 1
    assert replaced == 1
    assert errors == []
    assert service.replaced_ids == [42]
    assert len(service.created_payloads) == 1
    assert service.created_payloads[0]["title"] == "New Doc"


@pytest.mark.asyncio
async def test_save_documents_falls_back_to_create_when_replace_target_gone():
    """replaces_id 指向的文件已被刪除（replace_document 回傳 False）時，改為新增一筆。"""
    service = _FakeDocumentService(replace_ok=False)
    docs = [
        {
            "index": 1,
            "title": "Doc",
            "content": "c",
            "subject": "health",
            "grade": "G4",
            "page_number": None,
            "chapter": "Chapter 1",
            "image_filename": None,
            "source_filename": "upload.xlsx",
            "replaces_id": 999,
        },
    ]

    created, replaced, errors = await save_documents(docs, service)

    assert created == 1
    assert replaced == 0
    assert errors == []


class _FakeSession:
    def __init__(self):
        self.rollback_calls = 0

    async def rollback(self):
        self.rollback_calls += 1


class _FailingOnFirstRowDocumentService:
    """第一筆 create_document 會丟例外，模擬儲存失敗；用來驗證失敗後有 rollback，
    且不會因為 session 卡在 aborted transaction 而讓後續每一筆都跟著失敗。"""

    def __init__(self):
        self.db = _FakeSession()
        self.created_payloads = []
        self._calls = 0

    async def create_document(self, payload):
        self._calls += 1
        if self._calls == 1:
            raise RuntimeError("simulated DB error on first row")
        self.created_payloads.append(payload)
        return {"id": 1, **payload}


@pytest.mark.asyncio
async def test_save_documents_rolls_back_after_row_failure_and_continues():
    service = _FailingOnFirstRowDocumentService()
    docs = [
        {
            "index": 1,
            "title": "Bad Doc",
            "content": "c",
            "subject": "health",
            "grade": "G4",
            "page_number": None,
            "chapter": "Chapter 1",
            "image_filename": None,
            "source_filename": "upload.xlsx",
            "replaces_id": None,
        },
        {
            "index": 2,
            "title": "Good Doc",
            "content": "c2",
            "subject": "health",
            "grade": "G4",
            "page_number": None,
            "chapter": "Chapter 2",
            "image_filename": None,
            "source_filename": "upload.xlsx",
            "replaces_id": None,
        },
    ]

    created, replaced, errors = await save_documents(docs, service)

    assert created == 1
    assert replaced == 0
    assert len(errors) == 1
    assert errors[0]["index"] == 1
    assert service.db.rollback_calls == 1
    assert len(service.created_payloads) == 1
    assert service.created_payloads[0]["title"] == "Good Doc"
