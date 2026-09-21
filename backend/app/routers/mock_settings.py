"""Mock 全域設定 API — 與真實版同 schema,不需 DB。"""
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.llm_models import DEFAULT_MODEL, MODEL_ALLOWLIST, validate_model

router = APIRouter(prefix="/api/settings", tags=["settings"])

_state = {"model": DEFAULT_MODEL, "recommended": [m["id"] for m in MODEL_ALLOWLIST]}


class SetModelRequest(BaseModel):
    model: str = Field(..., min_length=1)


class RecommendedRequest(BaseModel):
    models: List[str] = Field(default_factory=list)


@router.get("/models", response_model=Dict[str, Any])
async def get_models_mock():
    names = {m["id"]: m["display_name"] for m in MODEL_ALLOWLIST}
    return {
        "models": [
            {"id": mid, "alias": mid, "display_name": names.get(mid, mid), "group": "recommended"}
            for mid in _state["recommended"]
        ]
    }


@router.get("/recommended", response_model=Dict[str, Any])
async def get_recommended_mock():
    return {"models": list(_state["recommended"])}


@router.put("/recommended", response_model=Dict[str, Any])
async def set_recommended_mock(request: RecommendedRequest):
    cleaned: List[str] = []
    for raw in request.models:
        mid = (raw or "").strip()
        if not mid or mid in cleaned:
            continue
        try:
            await validate_model(mid)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        cleaned.append(mid)
    _state["recommended"] = cleaned
    return {"models": cleaned}


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
