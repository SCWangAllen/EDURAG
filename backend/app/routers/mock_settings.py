"""Mock 全域設定 API — 與真實版同 schema,不需 DB。"""
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.llm_models import DEFAULT_MODEL, MODEL_ALLOWLIST, validate_model

router = APIRouter(prefix="/api/settings", tags=["settings"])

_state = {"model": DEFAULT_MODEL}


class SetModelRequest(BaseModel):
    model: str = Field(..., min_length=1)


@router.get("/models", response_model=Dict[str, Any])
async def get_models_mock():
    return {"models": [{**m, "group": "recommended"} for m in MODEL_ALLOWLIST]}


@router.get("/model", response_model=Dict[str, str])
async def get_model_mock():
    return {"model": _state["model"]}


@router.put("/model", response_model=Dict[str, str])
async def set_model_mock(request: SetModelRequest):
    try:
        await validate_model(request.model.strip())  # mock 模式:格式正確即可
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    _state["model"] = request.model.strip()
    return {"model": _state["model"]}
