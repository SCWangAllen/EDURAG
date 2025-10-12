from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.question_service import QuestionService, MockQuestionService
from app.schemas.question import (
    QuestionCreate, QuestionUpdate, QuestionResponse, 
    QuestionListResponse, QuestionStatsResponse, QuestionExportRequest
)
from app.core.config import USE_MOCK_API
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_question_service(db: AsyncSession = Depends(get_db)) -> QuestionService:
    """獲取問題服務實例"""
    if USE_MOCK_API:
        return MockQuestionService()
    return QuestionService(db)


@router.get("/", response_model=QuestionListResponse)
async def get_questions(
    subject: Optional[str] = Query(None, description="科目篩選"),
    grade: Optional[str] = Query(None, description="年級篩選 (G1-G6, ALL)"),
    question_type: Optional[str] = Query(None, description="題目類型篩選"),
    difficulty: Optional[str] = Query(None, description="難度篩選"),
    search: Optional[str] = Query(None, description="搜尋關鍵字"),
    page: int = Query(1, ge=1, description="頁碼"),
    size: int = Query(20, ge=1, le=100, description="每頁數量"),
    service: QuestionService = Depends(get_question_service)
):
    """取得問題清單"""
    try:
        skip = (page - 1) * size
        result = await service.get_questions(
            skip=skip,
            limit=size,
            subject=subject,
            grade=grade,
            question_type=question_type,
            difficulty=difficulty,
            search=search
        )

        logger.info(f"Retrieved {len(result.questions)} questions (total: {result.total}, grade: {grade})")
        return result

    except Exception as e:
        logger.error(f"Error getting questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=QuestionResponse)
async def create_question(
    question_data: QuestionCreate,
    service: QuestionService = Depends(get_question_service)
):
    """創建新問題"""
    try:
        result = await service.create_question(question_data)
        logger.info(f"Created question with ID: {result.id}")
        return result
        
    except Exception as e:
        logger.error(f"Error creating question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=QuestionStatsResponse)
async def get_question_stats(
    service: QuestionService = Depends(get_question_service)
):
    """取得問題統計"""
    try:
        stats = await service.get_question_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting question stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    service: QuestionService = Depends(get_question_service)
):
    """取得單一問題詳情"""
    try:
        question = await service.get_question_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="問題不存在")
            
        return question
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting question {question_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    service: QuestionService = Depends(get_question_service)
):
    """更新問題"""
    try:
        updated_question = await service.update_question(question_id, question_data)
        if not updated_question:
            raise HTTPException(status_code=404, detail="問題不存在")
            
        return updated_question
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating question {question_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{question_id}")
async def delete_question(
    question_id: int,
    service: QuestionService = Depends(get_question_service)
):
    """刪除問題"""
    try:
        success = await service.delete_question(question_id)
        if not success:
            raise HTTPException(status_code=404, detail="問題不存在")
            
        return {"message": "問題已刪除", "question_id": question_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting question {question_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
async def export_questions(
    export_request: QuestionExportRequest,
    service: QuestionService = Depends(get_question_service)
):
    """導出問題"""
    try:
        if USE_MOCK_API:
            # Mock 模式簡單返回示例數據
            return {
                "message": "導出功能在 Mock 模式下不可用",
                "format": export_request.format,
                "filters": {
                    "subject": export_request.subject,
                    "question_type": export_request.question_type,
                    "difficulty": export_request.difficulty
                }
            }
        
        result = await service.export_questions(
            format=export_request.format,
            subject=export_request.subject,
            question_type=export_request.question_type,
            difficulty=export_request.difficulty
        )
        
        return Response(
            content=result["content"],
            media_type=result["content_type"],
            headers={"Content-Disposition": f"attachment; filename={result['filename']}"}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))