"""複製文件到其他年級的規劃邏輯測試。

plan_document_copies 是純函式（不觸 DB），比對正規化科目 + 年級 + 章節 + 標題 + 頁碼，
用來決定「複製到其他年級」時該新增哪些文件、略過哪些 (文件, 目標年級) 組合。
copy_documents_to_grades（DocumentService 方法）另外處理 DB 查詢/寫入，不在此測試範圍
（需要真的 DB session，超出 mock 模式單元測試範圍）。
"""
from app.services.document_service import plan_document_copies


def _doc(
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


def _existing_row(
    id_,
    subject="health",
    grade="JR4",
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


class TestPlanDocumentCopies:
    def test_same_grade_is_skipped(self):
        """目標年級與來源文件自身年級相同時應略過，不重複複製到同一年級。"""
        docs = [_doc(1, grade="G4")]

        to_create, skipped = plan_document_copies([], docs, ["G4"])

        assert to_create == []
        assert skipped == [{"document_id": 1, "grade": "G4", "reason": "same grade"}]

    def test_existing_target_document_is_skipped(self):
        """目標年級已有正規化後完全相同（科目+年級+章節+標題+頁碼）的文件時應略過。"""
        docs = [_doc(1, grade="G4")]
        existing = [_existing_row(99, grade="JR4")]

        to_create, skipped = plan_document_copies(existing, docs, ["JR4"])

        assert to_create == []
        assert skipped == [{"document_id": 1, "grade": "JR4", "reason": "exists"}]

    def test_normal_copy_is_planned(self):
        """一般情況：目標年級不同且無既有文件命中，應排入 to_create。"""
        docs = [_doc(1, grade="G4")]

        to_create, skipped = plan_document_copies([], docs, ["JR4"])

        assert skipped == []
        assert len(to_create) == 1
        assert to_create[0]["grade"] == "JR4"
        assert to_create[0]["source"]["id"] == 1

    def test_multiple_target_grades_mix_of_create_and_skip(self):
        """同一份文件複製到多個目標年級時，各年級各自獨立判斷。"""
        docs = [_doc(1, grade="G4")]
        existing = [_existing_row(99, grade="JR5")]

        to_create, skipped = plan_document_copies(existing, docs, ["G4", "JR4", "JR5"])

        assert skipped == [
            {"document_id": 1, "grade": "G4", "reason": "same grade"},
            {"document_id": 1, "grade": "JR5", "reason": "exists"},
        ]
        assert len(to_create) == 1
        assert to_create[0]["grade"] == "JR4"

    def test_case_and_whitespace_insensitive_matching_against_existing(self):
        """既有資料的科目/章節/標題/頁碼比對大小寫與前後空白不敏感（沿用 _match_key 語意）。"""
        docs = [
            _doc(
                1,
                subject="Health",
                chapter="  Chapter 4  ",
                title="body defenses",
                page_number=" 1 ",
            )
        ]
        existing = [_existing_row(99, subject="health", grade="JR4")]

        to_create, skipped = plan_document_copies(existing, docs, ["JR4"])

        assert to_create == []
        assert skipped == [{"document_id": 1, "grade": "JR4", "reason": "exists"}]

    def test_duplicate_target_within_same_batch_only_creates_once(self):
        """同一批次內兩份不同來源文件複製到同一目標年級後產生相同 key，
        第二個應被視為與第一個新建結果重複而略過，避免同一請求內建立兩筆完全相同的文件。"""
        docs = [
            _doc(
                1,
                subject="health",
                grade="G4",
                chapter="Chapter 4",
                title="Body Defenses",
                page_number="1",
            ),
            _doc(
                2,
                subject="health",
                grade="G5",
                chapter="Chapter 4",
                title="Body Defenses",
                page_number="1",
            ),
        ]

        to_create, skipped = plan_document_copies([], docs, ["JR4"])

        assert len(to_create) == 1
        assert to_create[0]["source"]["id"] == 1
        assert skipped == [{"document_id": 2, "grade": "JR4", "reason": "exists"}]
