"""全域設定 API — 可選模型清單與目前使用模型。"""
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm_models import list_models
from app.db.database import get_db
from app.services.settings_service import SettingsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SetModelRequest(BaseModel):
    model: str = Field(..., min_length=1, description="要使用的模型 id")


@router.get("/models", response_model=Dict[str, Any])
async def get_models():
    """可選模型清單(Anthropic live + 精選過濾,失敗 fallback 硬清單)。"""
    return {"models": await list_models()}


@router.get("/model", response_model=Dict[str, str])
async def get_model(db: AsyncSession = Depends(get_db)):
    """目前使用中的生成模型。"""
    return {"model": await SettingsService(db).get_model()}


@router.put("/model", response_model=Dict[str, str])
async def set_model(request: SetModelRequest, db: AsyncSession = Depends(get_db)):
    """設定生成模型(非精選清單內的值回 400)。"""
    try:
        model = await SettingsService(db).set_model(request.model)
        return {"model": model}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("設定模型失敗: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
