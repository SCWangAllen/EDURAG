"""
Excel 上傳 Service — 從 routers/upload.py 提取的業務邏輯。
"""
import logging
from typing import List, Dict, Any, Optional, TYPE_CHECKING

import pandas as pd
import io

from app.services.document_service import DocumentService
from app.core.config import UPLOAD_CHUNK_SIZE, CHUNK_OVERLAP
from app.core.subject_norm import normalize_grade, normalize_subject

if TYPE_CHECKING:
    from app.services.subject_service import SubjectService

logger = logging.getLogger(__name__)


def generate_content_chunks(
    content: str,
    chunk_size: int = UPLOAD_CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    """將長文本分割成較小的塊（用於 RAG 系統）"""
    if len(content) <= chunk_size:
        return [
            {
                "chunk_index": 1,
                "text": content,
                "start_pos": 0,
                "end_pos": len(content),
                "length": len(content),
            }
        ]

    chunks: List[Dict[str, Any]] = []
    start = 0
    chunk_index = 1

    while start < len(content):
        end = min(start + chunk_size, len(content))

        if end < len(content):
            for break_char in ["。", "\\n", ".", "!", "?"]:
                last_break = content.rfind(break_char, start, end)
                if last_break > start:
                    end = last_break + 1
                    break

        chunk_text = content[start:end].strip()
        if chunk_text:
            chunks.append(
                {
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                    "start_pos": start,
                    "end_pos": end,
                    "length": len(chunk_text),
                }
            )
            chunk_index += 1

        start = max(end - overlap, start + 1)

    return chunks


def parse_excel(contents: bytes, filename: str) -> List[Dict[str, Any]]:
    """
    解析 Excel 文件，回傳 processed_documents 列表。
    """
    df = pd.read_excel(io.BytesIO(contents))

    logger.info("成功讀取 Excel 文件 %s，包含 %d 筆資料", filename, len(df))

    required_columns = ["Words", "Chapter", "Subject", "Imagesrelated"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(
            f"Excel 文件缺少必要欄位: {', '.join(missing_columns)}"
        )

    processed_documents: List[Dict[str, Any]] = []
    for index, row in df.iterrows():
        # 逐列軟性驗證警示(穩定代碼,前端對應 i18n;不改變照存行為)
        warnings: List[str] = []

        content = str(row["Words"]) if pd.notna(row["Words"]) else ""
        if not content.strip():
            warnings.append("content_empty")

        chapter = str(row["Chapter"]) if pd.notna(row["Chapter"]) else ""
        if not chapter.strip():
            warnings.append("chapter_empty")

        if pd.notna(row["Subject"]):
            subject = normalize_subject(row["Subject"])
        else:
            subject = "health"
            warnings.append("subject_defaulted")

        image_filename = (
            str(row["Imagesrelated"]) if pd.notna(row["Imagesrelated"]) else None
        )

        grade = None
        if "Grade" in df.columns and pd.notna(row["Grade"]):
            grade = normalize_grade(row["Grade"]) or None
            if grade is None:
                warnings.append("grade_invalid")

        page_number = None
        if "Page" in df.columns and pd.notna(row["Page"]):
            page_number = str(row["Page"]).strip()

        if chapter:
            # chapter 全文保存；title 僅取首行並截到欄位上限 200（顯示用）
            first_line = chapter.split("\\n")[0] if "\\n" in chapter else chapter
            title = first_line[:200]
        else:
            title = content[:50] + "..." if len(content) > 50 else content

        chunks = generate_content_chunks(content)

        doc_data = {
            "index": index + 1,
            "title": title.strip(),
            "content": content,
            "subject": subject,
            "grade": grade,
            "page_number": page_number,
            "chapter": chapter,
            "image_filename": image_filename,
            "chunks": chunks,
            "chunk_count": len(chunks),
            "content_length": len(content),
            "warnings": warnings,
        }
        processed_documents.append(doc_data)

    return processed_documents


async def save_documents(
    processed_documents: List[Dict[str, Any]],
    service: DocumentService,
    subject_service: Optional["SubjectService"] = None,
) -> tuple[int, List[Dict[str, Any]]]:
    """批量儲存文件到資料庫，回傳 (成功數量, 失敗清單)。

    失敗不可靜默：每筆失敗記錄 {index, title, error} 回報給呼叫端。
    """
    saved_count = 0
    errors: List[Dict[str, Any]] = []
    created_subjects: set[str] = set()  # 追蹤已建立的科目，避免重複查詢

    for doc_data in processed_documents:
        try:
            subject_name = doc_data["subject"]

            # 自動建立科目（若不存在）
            if subject_service and subject_name not in created_subjects:
                success = await _ensure_subject_exists(subject_service, subject_name)
                if success:
                    created_subjects.add(subject_name)
                # 即使科目建立失敗，仍繼續儲存文件（文件的 subject 欄位是文字，非外鍵）

            await service.create_document(
                {
                    "title": doc_data["title"],
                    "content": doc_data["content"],
                    "subject": doc_data["subject"],
                    "grade": doc_data.get("grade"),
                    "page_number": doc_data.get("page_number"),
                    "chapter": doc_data["chapter"],
                    "image_filename": doc_data["image_filename"],
                    "import_source": "excel_upload",
                }
            )
            saved_count += 1
        except Exception as e:
            logger.error("儲存第 %d 筆資料失敗: %s", doc_data["index"], e)
            errors.append(
                {
                    "index": doc_data["index"],
                    "title": doc_data.get("title", ""),
                    "error": str(e),
                }
            )
    return saved_count, errors


async def _ensure_subject_exists(
    subject_service: "SubjectService",
    subject_name: str,
) -> bool:
    """檢查科目是否存在，若不存在則自動建立。回傳是否成功。"""
    from app.schemas.subject import SubjectCreate

    try:
        existing = await subject_service.get_subject_by_name(subject_name)
        if existing:
            return True

        await subject_service.create_subject(
            SubjectCreate(
                name=subject_name,
                description="自動建立於 Excel 匯入",
                color="#3B82F6",
            )
        )
        logger.info("自動建立科目: %s", subject_name)
        return True
    except ValueError as e:
        # 科目可能被另一個並行請求建立，檢查是否為「已存在」錯誤
        if "已存在" in str(e):
            logger.debug("科目 %s 已存在（並行建立）", subject_name)
            return True
        logger.warning("建立科目 %s 失敗: %s", subject_name, e)
        return False
    except Exception as e:
        logger.warning("建立科目 %s 失敗: %s", subject_name, e)
        return False
