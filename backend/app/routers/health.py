from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db.database import get_db
from app.core.config import USE_MOCK_API
import sys

router = APIRouter(tags=["health"])

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    mode: str
    database_connected: bool
    python_version: str

@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """健康檢查端點"""
    database_connected = True
    
    if not USE_MOCK_API:
        try:
            # 簡單的資料庫連線測試
            await db.execute(text("SELECT 1"))
        except Exception:
            database_connected = False
    
    return HealthResponse(
        status="healthy" if database_connected else "degraded",
        version="1.0.0",
        timestamp=datetime.now(),
        mode="mock" if USE_MOCK_API else "production",
        database_connected=database_connected,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )