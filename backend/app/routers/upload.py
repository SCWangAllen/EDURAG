from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.document_service import DocumentService
from app.services.subject_service import SubjectService
from app.services.upload_service import parse_excel, save_documents
from typing import Dict, Any
import pandas as pd
import io
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])


async def get_document_service(
    db: AsyncSession = Depends(get_db),
) -> DocumentService:
    return DocumentService(db)


async def get_subject_service(
    db: AsyncSession = Depends(get_db),
) -> SubjectService:
    return SubjectService(db)


@router.post("/excel")
async def upload_excel(
    file: UploadFile = File(...),
    preview_only: bool = Form(False),
    service: DocumentService = Depends(get_document_service),
    subject_service: SubjectService = Depends(get_subject_service),
) -> Dict[str, Any]:
    """上傳 Excel 文件並解析"""
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400, detail="只支援 Excel 文件 (.xlsx, .xls)"
        )

    try:
        contents = await file.read()
        processed_documents = parse_excel(contents, file.filename)

        if preview_only:
            return {
                "message": f"成功解析 Excel 文件，包含 {len(processed_documents)} 筆資料",
                "file_name": file.filename,
                "total_documents": len(processed_documents),
                "documents": processed_documents,
                "preview_mode": True,
            }

        saved_count = await save_documents(
            processed_documents, service, subject_service
        )

        return {
            "message": f"成功上傳並儲存 {saved_count} 筆文件",
            "file_name": file.filename,
            "total_documents": len(processed_documents),
            "saved_documents": saved_count,
            "documents": processed_documents[:5],
            "preview_mode": False,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=400, detail="Excel 文件為空或格式錯誤"
        )
    except Exception as e:
        logger.error("處理 Excel 文件時發生錯誤: %s", e)
        raise HTTPException(
            status_code=500, detail=f"處理文件時發生錯誤: {str(e)}"
        )


@router.get("/template")
async def get_excel_template():
    """下載 Excel 範本文件"""
    template_data = {
        "Words": [
            "Your body's Defenses 71\nPrevention by Stopping the Spread of Pathogens\n"
            "Pathogens live in the air and on surfaces...",
            "0 Developing Good Health\nbody needs. Vitamin C and the mineral zinc are "
            "especially important...",
        ],
        "Chapter": [
            "Chapter 4  Your Body's Defenses",
            "Chapter 4  Your Body's Defenses",
        ],
        "Subject": ["Health", "Health"],
        "Grade": ["G4", "G4"],
        "Page": ["71", "70"],
        "Imagesrelated": ["G4Health71.jpg", None],
    }

    df = pd.DataFrame(template_data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="工作表1", index=False)

    output.seek(0)

    return StreamingResponse(
        io.BytesIO(output.read()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=document_template.xlsx"
        },
    )
