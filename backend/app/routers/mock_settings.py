"""Mock 全域設定 API — 與真實版同 schema,不需 DB。"""
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.llm_models import DEFAULT_MODEL, MODEL_ALLOWLIST, is_allowed_model

router = APIRouter(prefix="/api/settings", tags=["settings"])

_state = {"model": DEFAULT_MODEL}


class SetModelRequest(BaseModel):
    model: str = Field(..., min_length=1)


@router.get("/models", response_model=Dict[str, Any])
async def get_models_mock():
    return {"models": [dict(m) for m in MODEL_ALLOWLIST]}


@router.get("/model", response_model=Dict[str, str])
async def get_model_mock():
    return {"model": _state["model"]}


@router.put("/model", response_model=Dict[str, str])
async def set_model_mock(request: SetModelRequest):
    if not is_allowed_model(request.model):
        raise HTTPException(status_code=400, detail=f"不支援的模型：{request.model}")
    _state["model"] = request.model
    return {"model": _state["model"]}
