from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.template_service import TemplateService
from app.schemas.template import (
    TemplateCreate, 
    TemplateUpdate, 
    TemplateResponse, 
    TemplateList
)
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/templates", tags=["templates"])

@router.get("/", response_model=TemplateList)
async def get_templates(
    subject: Optional[str] = Query(None, description="科目篩選"),
    page: int = Query(1, ge=1, description="頁碼"),
    size: int = Query(20, ge=1, le=100, description="每頁數量"),
    db: AsyncSession = Depends(get_db)
):
    """取得模板清單"""
    skip = (page - 1) * size
    
    service = TemplateService(db)
    templates = await service.get_templates(subject=subject, skip=skip, limit=size)
    total = await service.get_templates_count(subject=subject)
    
    return TemplateList(
        templates=[TemplateResponse.from_orm(t) for t in templates],
        total=total,
        page=page,
        size=size
    )

@router.get("/subjects")
async def get_subjects(db: AsyncSession = Depends(get_db)):
    """取得所有科目清單"""
    service = TemplateService(db)
    subjects = await service.get_subjects()
    return {"subjects": subjects}

@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """取得單一模板詳情"""
    service = TemplateService(db)
    template = await service.get_template_by_id(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    return TemplateResponse.from_orm(template)

@router.post("/", response_model=TemplateResponse)
async def create_template(
    template_data: TemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """建立新模板"""
    try:
        logger.info(f"Creating template with data: {template_data}")
        service = TemplateService(db)
        template = await service.create_template(template_data)
        
        return TemplateResponse.from_orm(template)
    
    except ValueError as e:
        logger.error(f"Validation error creating template: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create template: {str(e)}")
        logger.exception("Template creation error details:")
        raise HTTPException(status_code=500, detail=f"建立模板失敗: {str(e)}")

@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新模板"""
    try:
        service = TemplateService(db)
        template = await service.update_template(template_id, template_data)
        
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        return TemplateResponse.from_orm(template)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update template: {str(e)}")
        raise HTTPException(status_code=500, detail="更新模板失敗")

@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """刪除模板"""
    try:
        service = TemplateService(db)
        success = await service.delete_template(template_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        return {"message": "模板已刪除", "template_id": template_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete template: {str(e)}")
        raise HTTPException(status_code=500, detail="刪除模板失敗")

@router.post("/initialize-defaults")
async def initialize_default_templates(db: AsyncSession = Depends(get_db)):
    """初始化預設模板（開發用）"""
    try:
        service = TemplateService(db)
        await service.initialize_default_templates()
        return {"message": "預設模板初始化完成"}
    
    except Exception as e:
        logger.error(f"Failed to initialize default templates: {str(e)}")
        raise HTTPException(status_code=500, detail="初始化預設模板失敗")