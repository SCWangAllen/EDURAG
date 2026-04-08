from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.document_service import DocumentService, MockDocumentService
from app.services.template_service import TemplateService, MockTemplateService
from app.services.dashboard_service import DashboardService
from app.core.config import USE_MOCK_API
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_document_service(
    db: AsyncSession = Depends(get_db),
) -> DocumentService:
    if USE_MOCK_API:
        return MockDocumentService()
    return DocumentService(db)


async def get_template_service(
    db: AsyncSession = Depends(get_db),
) -> TemplateService:
    if USE_MOCK_API:
        return MockTemplateService()
    return TemplateService(db)


@router.get("/stats", response_model=Dict[str, Any])
async def get_dashboard_stats(
    document_service: DocumentService = Depends(get_document_service),
    template_service: TemplateService = Depends(get_template_service),
    db: AsyncSession = Depends(get_db),
):
    """取得儀表板統計資料"""
    try:
        service = DashboardService(db, document_service, template_service)
        return await service.get_stats()
    except Exception as e:
        logger.error("Error getting dashboard stats: %s", e)
        return {
            "templates": 0,
            "documents": 0,
            "questions": 0,
            "subjects": 0,
            "error": str(e),
        }
