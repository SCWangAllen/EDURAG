from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=Dict[str, Any])
async def get_dashboard_stats():
    """取得儀表板統計資料 (Mock 模式)"""
    return {
        "templates": 4,
        "documents": 16,
        "questions": 48,
        "subjects": 4,
        "document_details": {
            "total_documents": 16,
            "subjects": {
                "Health": 13,
                "健康": 1,
                "英文": 1,
                "歷史": 1
            },
            "top_chapters": {
                "Chapter 1": 3,
                "Chapter 2": 2,
                "Chapter 3": 2
            },
            "has_images": 7
        },
        "system_status": {
            "backend_api": "running",
            "template_system": "running", 
            "database": "mock_mode"
        }
    }