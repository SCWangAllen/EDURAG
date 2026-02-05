"""
Excel 上傳 Service — 從 routers/upload.py 提取的業務邏輯。
"""
import logging
from typing import List, Dict, Any, Optional

import pandas as pd
import io

from app.services.document_service import DocumentService
from app.core.config import UPLOAD_CHUNK_SIZE, CHUNK_OVERLAP

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
        content = str(row["Words"]) if pd.notna(row["Words"]) else ""
        chapter = str(row["Chapter"]) if pd.notna(row["Chapter"]) else ""
        subject = str(row["Subject"]) if pd.notna(row["Subject"]) else "健康"
        image_filename = (
            str(row["Imagesrelated"]) if pd.notna(row["Imagesrelated"]) else None
        )

        grade = None
        if "Grade" in df.columns and pd.notna(row["Grade"]):
            grade_value = str(row["Grade"]).strip().upper()
            if grade_value in ["G1", "G2", "G3", "G4", "G5", "G6", "ALL"]:
                grade = grade_value
            else:
                logger.warning(
                    "第 %d 行的 Grade 值 '%s' 格式不正確，將被忽略",
                    index + 1,
                    grade_value,
                )

        page_number = None
        if "Page" in df.columns and pd.notna(row["Page"]):
            page_number = str(row["Page"]).strip()

        if chapter:
            title = (
                chapter.split("\\n")[0][:100]
                if "\\n" in chapter
                else chapter[:100]
            )
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
        }
        processed_documents.append(doc_data)

    return processed_documents


async def save_documents(
    processed_documents: List[Dict[str, Any]],
    service: DocumentService,
) -> int:
    """批量儲存文件到資料庫，回傳成功數量。"""
    saved_count = 0
    for doc_data in processed_documents:
        try:
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
    return saved_count
