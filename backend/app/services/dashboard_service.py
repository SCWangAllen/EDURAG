"""
Dashboard Service — 從 routers/dashboard.py 提取的統計查詢邏輯。
"""
import logging
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.models import Question
from app.services.document_service import DocumentService, MockDocumentService
from app.services.template_service import TemplateService, MockTemplateService
from app.core.config import USE_MOCK_API

logger = logging.getLogger(__name__)


class DashboardService:
    def __init__(
        self,
        db: AsyncSession,
        document_service: DocumentService,
        template_service: TemplateService,
    ):
        self.db = db
        self.document_service = document_service
        self.template_service = template_service

    async def get_stats(self) -> Dict[str, Any]:
        doc_stats = await self.document_service.get_document_stats()

        templates = await self.template_service.get_templates()

        if USE_MOCK_API:
            subjects = ["Health", "健康", "英文", "歷史"]
        else:
            subjects = await self.document_service.get_subjects()

        questions_count = 0
        if USE_MOCK_API:
            questions_count = 48
        else:
            try:
                count_stmt = select(func.count(Question.id))
                count_result = await self.db.execute(count_stmt)
                questions_count = count_result.scalar() or 0
            except Exception as e:
                logger.warning("Failed to get questions count: %s", e)

        return {
            "templates": len(templates),
            "documents": doc_stats.get("total_documents", 0),
            "questions": questions_count,
            "subjects": len(subjects),
            "document_details": doc_stats,
            "system_status": {
                "backend_api": "running",
                "template_system": "running",
                "database": "running" if not USE_MOCK_API else "mock_mode",
            },
        }
