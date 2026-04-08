"""圖片題目管理 API 端點"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Union
import logging

from app.db.database import get_db
from app.core.config import USE_MOCK_API
from app.services.image_question_service import ImageQuestionService, MockImageQuestionService
from app.services.subject_service import SubjectService
from app.schemas.image_question import (
    ImageQuestionCreate,
    ImageQuestionUpdate,
    ImageQuestionResponse,
    ImageQuestionListResponse,
    ImageQuestionStatsResponse,
    ImageUploadPreview,
    ImageVerifyRequest,
    ImageVerifyResponse,
    MissingImagesResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/image-questions", tags=["image-questions"])

# 檔案大小限制（50MB）
MAX_FILE_SIZE = 50 * 1024 * 1024


async def get_image_question_service(
    db: AsyncSession = Depends(get_db),
) -> Union[ImageQuestionService, MockImageQuestionService]:
    """取得圖片題目服務實例"""
    if USE_MOCK_API:
        return MockImageQuestionService()
    return ImageQuestionService(db)


async def get_subject_service(
    db: AsyncSession = Depends(get_db),
) -> SubjectService:
    """取得科目服務實例"""
    return SubjectService(db)


@router.post("/", response_model=ImageQuestionResponse)
async def create_question(
    data: ImageQuestionCreate,
    service: Union[ImageQuestionService, MockImageQuestionService] = Depends(get_image_question_service),
    subject_service: SubjectService = Depends(get_subject_service),
):
    """創建單一圖片題目

    若科目不存在，將自動創建
    """
    try:
        if isinstance(service, MockImageQuestionService):
            return await service.create_single(data)

        result = await service.create_single(data, subject_service=subject_service)
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"創建圖片題目時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/excel", response_model=ImageUploadPreview)
async def upload_excel(
    file: UploadFile = File(...),
    preview_only: bool = Form(True),
    service: Union[ImageQuestionService, MockImageQuestionService] = Depends(get_image_question_service),
    subject_service: SubjectService = Depends(get_subject_service),
):
    """上傳 Excel 檔案匯入圖片題目

    - preview_only=True: 只預覽不儲存
    - preview_only=False: 預覽並儲存有效資料
    - 自動創建不存在的科目
    """
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400, detail="只支援 Excel 檔案 (.xlsx, .xls)"
        )

    try:
        contents = await file.read()

        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"檔案太大，最大允許 {MAX_FILE_SIZE // (1024 * 1024)}MB"
            )

        preview = service.parse_excel(contents, file.filename)

        if preview_only:
            return preview

        if preview.valid_rows > 0:
            if isinstance(service, MockImageQuestionService):
                saved_count = await service.create_batch(preview.items)
            else:
                saved_count = await service.create_batch(
                    preview.items, subject_service=subject_service
                )
            logger.info(f"成功儲存 {saved_count} 筆圖片題目")

        return preview

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"處理 Excel 時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"處理檔案時發生錯誤: {str(e)}")


@router.get("/", response_model=ImageQuestionListResponse)
async def get_questions(
    subject: Optional[str] = Query(None, description="科目篩選"),
    grade: Optional[str] = Query(None, description="年級篩選 (G1-G6)"),
    chapter: Optional[str] = Query(None, description="章節篩選"),
    verified: Optional[bool] = Query(None, description="圖片是否已驗證"),
    search: Optional[str] = Query(None, description="搜尋關鍵字"),
    page: int = Query(1, ge=1, description="頁碼"),
    size: int = Query(20, ge=1, le=100, description="每頁數量"),
    service: ImageQuestionService = Depends(get_image_question_service),
):
    """取得圖片題目清單"""
    try:
        skip = (page - 1) * size
        result = await service.get_questions(
            skip=skip,
            limit=size,
            subject=subject,
            grade=grade,
            chapter=chapter,
            verified=verified,
            search=search,
        )
        logger.info(f"取得 {len(result.questions)} 筆圖片題目")
        return result

    except Exception as e:
        logger.error(f"取得圖片題目時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=ImageQuestionStatsResponse)
async def get_stats(
    service: ImageQuestionService = Depends(get_image_question_service),
):
    """取得圖片題目統計"""
    try:
        stats = await service.get_stats()
        return stats

    except Exception as e:
        logger.error(f"取得統計時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/missing-images", response_model=MissingImagesResponse)
async def get_missing_images(
    service: ImageQuestionService = Depends(get_image_question_service),
):
    """取得所有缺失圖片的題目清單

    返回格式:
    - missing_question_images: 問題圖片缺失的題目清單
    - missing_answer_images: 答案圖片缺失的題目清單
    - total_missing: 總缺失數量
    """
    try:
        result = await service.get_missing_images()
        return result

    except Exception as e:
        logger.error(f"取得缺失圖片清單時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{question_id}", response_model=ImageQuestionResponse)
async def get_question(
    question_id: int,
    service: ImageQuestionService = Depends(get_image_question_service),
):
    """取得單一圖片題目"""
    try:
        question = await service.get_question_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="圖片題目不存在")
        return question

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取得圖片題目 {question_id} 時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{question_id}", response_model=ImageQuestionResponse)
async def update_question(
    question_id: int,
    data: ImageQuestionUpdate,
    service: ImageQuestionService = Depends(get_image_question_service),
):
    """更新圖片題目"""
    try:
        updated = await service.update_question(question_id, data)
        if not updated:
            raise HTTPException(status_code=404, detail="圖片題目不存在")
        return updated

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新圖片題目 {question_id} 時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{question_id}")
async def delete_question(
    question_id: int,
    service: ImageQuestionService = Depends(get_image_question_service),
):
    """刪除圖片題目"""
    try:
        success = await service.delete_question(question_id)
        if not success:
            raise HTTPException(status_code=404, detail="圖片題目不存在")
        return {"message": "圖片題目已刪除", "question_id": question_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刪除圖片題目 {question_id} 時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-images", response_model=ImageVerifyResponse)
async def verify_images(
    request: ImageVerifyRequest,
    service: ImageQuestionService = Depends(get_image_question_service),
):
    """驗證指定題目的圖片是否存在"""
    try:
        result = await service.verify_images(request.question_ids)
        return result

    except Exception as e:
        logger.error(f"驗證圖片時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))
