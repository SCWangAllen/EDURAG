from fastapi import APIRouter, HTTPException, Query
from app.services.template_service import MockTemplateService
from app.schemas.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateMoveRequest,
    TemplateMoveResponse,
    TemplateMoveToRequest,
    TemplateMoveToResponse,
)
from typing import Literal, Optional

router = APIRouter(prefix="/api/templates", tags=["templates"])

# 全域 Mock 服務實例
mock_service = MockTemplateService()

@router.get("/")
async def get_templates(
    subject: Optional[str] = Query(None, description="科目篩選"),
    search: Optional[str] = Query(None, description="搜尋關鍵字（比對模板名稱或內容）"),
    sort: Literal["grade", "newest", "manual"] = Query(
        "grade", description="排序方式：grade（預設）｜newest｜manual"
    ),
    page: int = Query(1, ge=1, description="頁碼"),
    size: int = Query(20, ge=1, le=100, description="每頁數量")
):
    """取得模板清單 (Mock)"""
    skip = (page - 1) * size

    templates = await mock_service.get_templates(
        subject=subject, search=search, sort=sort, skip=skip, limit=size
    )
    total = await mock_service.get_templates_count(subject=subject, search=search)

    return {
        "templates": templates,
        "total": total,
        "page": page,
        "size": size
    }

@router.get("/subjects")
async def get_subjects():
    """取得所有科目清單 (Mock)"""
    subjects = await mock_service.get_subjects()
    return {"subjects": subjects}

@router.post("/{template_id}/move", response_model=TemplateMoveResponse)
async def move_template(template_id: int, move_data: TemplateMoveRequest):
    """上移 / 下移一格（Mock）"""
    result = await mock_service.move_template(template_id, move_data.direction)

    if result is None:
        raise HTTPException(status_code=404, detail="模板不存在")

    return TemplateMoveResponse(
        moved=result["moved"],
        template_id=template_id,
        sort_order=result["sort_order"],
    )

@router.post("/{template_id}/move-to", response_model=TemplateMoveToResponse)
async def move_template_to(template_id: int, move_data: TemplateMoveToRequest):
    """拖曳排序:把模板移到任意位置（Mock）"""
    result = await mock_service.move_template_to(
        template_id, before_id=move_data.before_id, after_id=move_data.after_id
    )

    if result is None:
        raise HTTPException(status_code=404, detail="模板不存在")

    return TemplateMoveToResponse(
        moved=result["moved"],
        template_id=template_id,
        order=result["order"],
    )

@router.get("/{template_id}")
async def get_template(template_id: int):
    """取得單一模板詳情 (Mock)"""
    template = await mock_service.get_template_by_id(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    return template

@router.post("/")
async def create_template(template_data: TemplateCreate):
    """建立新模板 (Mock)"""
    try:
        template = await mock_service.create_template(template_data.dict())
        return template
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"建立模板失敗: {str(e)}")

@router.put("/{template_id}")
async def update_template(template_id: int, template_data: TemplateUpdate):
    """更新模板 (Mock)"""
    template = await mock_service.get_template_by_id(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 更新 Mock 資料
    update_data = template_data.dict(exclude_unset=True)
    template.update(update_data)
    
    return template

@router.delete("/{template_id}")
async def delete_template(template_id: int):
    """刪除模板 (Mock)"""
    template = await mock_service.get_template_by_id(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # Mock 軟刪除
    template["is_active"] = "false"
    
    return {"message": "模板已刪除", "template_id": template_id}

@router.post("/initialize-defaults")
async def initialize_default_templates():
    """初始化預設模板 (Mock)"""
    return {"message": "預設模板初始化完成 (Mock 模式)"}