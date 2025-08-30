from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.database import get_db
from app.db.models import Question
from app.services.document_service import DocumentService, MockDocumentService
from app.services.template_service import TemplateService, MockTemplateService
from app.core.config import USE_MOCK_API
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_document_service(db: AsyncSession = Depends(get_db)) -> DocumentService:
    """獲取文件服務實例"""
    if USE_MOCK_API:
        return MockDocumentService()
    return DocumentService(db)

async def get_template_service(db: AsyncSession = Depends(get_db)) -> TemplateService:
    """獲取模板服務實例"""
    if USE_MOCK_API:
        return MockTemplateService()
    return TemplateService(db)


@router.get("/stats", response_model=Dict[str, Any])
async def get_dashboard_stats(
    document_service: DocumentService = Depends(get_document_service),
    template_service: TemplateService = Depends(get_template_service),
    db: AsyncSession = Depends(get_db)
):
    """取得儀表板統計資料"""
    try:
        # 取得文件統計
        doc_stats = await document_service.get_document_stats()
        
        # 取得模板統計
        templates = await template_service.get_templates()
        
        # 取得科目數量
        if USE_MOCK_API:
            subjects = ['Health', '健康', '英文', '歷史']
        else:
            subjects = await document_service.get_subjects()
        
        # 取得問題統計
        questions_count = 0
        if USE_MOCK_API:
            questions_count = 48  # Mock 資料
        else:
            # 真實模式從資料庫計算問題數量
            try:
                count_stmt = select(func.count(Question.id))
                count_result = await db.execute(count_stmt)
                questions_count = count_result.scalar() or 0
            except Exception as e:
                logger.warning(f"Failed to get questions count: {e}")
                questions_count = 0
        
        return {
            "templates": len(templates),
            "documents": doc_stats.get("total_documents", 0),
            "questions": questions_count,
            "subjects": len(subjects),
            "document_details": doc_stats,
            "system_status": {
                "backend_api": "running",
                "template_system": "running",
                "database": "running" if not USE_MOCK_API else "mock_mode"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        # 如果發生錯誤，返回基本資料
        return {
            "templates": 0,
            "documents": 0,
            "questions": 0,
            "subjects": 0,
            "error": str(e)
        }