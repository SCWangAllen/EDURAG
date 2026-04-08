import asyncio
import time
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import database
from app.schemas.question import (
    GenerateRequest,
    GenerateResponse,
    BatchGenerateRequest,
    BatchGenerateResponse,
    TemplateGenerateRequest,
    TemplateGenerateResponse,
    BatchTemplateGenerateRequest,
    BatchTemplateGenerateResponse,
    PromptGenerateRequest,
    PromptGenerateResponse,
    TemplateEnhancedGenerateRequest,
    TemplateEnhancedGenerateResponse,
)
from app.services.generate_service import GenerateService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/generate", tags=["generate"])


def _get_service(db: AsyncSession = Depends(database.get_db)) -> GenerateService:
    return GenerateService(db)


@router.post("/", response_model=GenerateResponse)
async def generate(
    req: GenerateRequest, service: GenerateService = Depends(_get_service)
):
    try:
        return await service.generate_basic(req)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"題目生成失敗: {str(e)}")


@router.post("/batch", response_model=BatchGenerateResponse)
async def generate_batch(
    req: BatchGenerateRequest, service: GenerateService = Depends(_get_service)
):
    start_time = time.time()
    results = []
    errors = []
    success_count = 0
    total_items = 0

    tasks = [service.generate_single(gen_req) for gen_req in req.generations]

    try:
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, result in enumerate(task_results):
            if isinstance(result, Exception):
                errors.append(f"請求 {i+1} 失敗: {str(result)}")
            else:
                results.append(result)
                success_count += 1
                total_items += result.count
    except Exception as e:
        errors.append(f"批次處理失敗: {str(e)}")

    return BatchGenerateResponse(
        results=results,
        total_items=total_items,
        total_time=time.time() - start_time,
        success_count=success_count,
        error_count=len(errors),
        errors=errors,
    )


@router.post("/template", response_model=TemplateGenerateResponse)
async def generate_template(
    req: TemplateGenerateRequest, service: GenerateService = Depends(_get_service)
):
    try:
        return await service.generate_from_template(req)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("模板生成失敗: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"模板生成失敗: {str(e)}")


@router.post("/template/batch", response_model=BatchTemplateGenerateResponse)
async def generate_template_batch(
    req: BatchTemplateGenerateRequest,
    service: GenerateService = Depends(_get_service),
):
    start_time = time.time()
    results = []
    errors = []
    success_count = 0
    total_items = 0

    tasks = [
        service.generate_from_template(gen_req) for gen_req in req.generations
    ]

    try:
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, result in enumerate(task_results):
            if isinstance(result, Exception):
                errors.append(f"請求 {i+1} 失敗: {str(result)}")
            else:
                results.append(result)
                success_count += 1
                total_items += result.count
    except Exception as e:
        errors.append(f"批次處理失敗: {str(e)}")

    return BatchTemplateGenerateResponse(
        results=results,
        total_items=total_items,
        total_time=time.time() - start_time,
        success_count=success_count,
        error_count=len(errors),
        errors=errors,
    )


@router.post("/prompt", response_model=PromptGenerateResponse)
async def generate_prompt(
    req: PromptGenerateRequest, service: GenerateService = Depends(_get_service)
):
    try:
        return await service.generate_from_prompt(req)
    except Exception as e:
        logger.error("Prompt 生成失敗: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prompt 生成失敗: {str(e)}")


@router.post("/template-enhanced", response_model=TemplateEnhancedGenerateResponse)
async def generate_template_enhanced(
    req: TemplateEnhancedGenerateRequest,
    service: GenerateService = Depends(_get_service),
):
    try:
        return await service.generate_template_enhanced(req)
    except Exception as e:
        logger.error("模板生成失敗: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"模板生成失敗: {str(e)}")
