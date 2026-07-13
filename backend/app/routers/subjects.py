from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.services.subject_service import SubjectService
from app.schemas.subject import (
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
    SubjectsListResponse,
    SubjectTreeResponse
)

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


@router.get("/", response_model=SubjectsListResponse)
async def get_subjects(
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """取得科目清單"""
    service = SubjectService(db)
    subjects = await service.get_subjects(include_inactive=include_inactive)
    
    return SubjectsListResponse(
        subjects=[SubjectResponse.from_orm(s) for s in subjects],
        total=len(subjects)
    )


# 注意：/tree 必須註冊在 /{subject_id}（int 轉換器）之前，否則會被吃掉回 422
@router.get("/tree", response_model=SubjectTreeResponse)
async def get_subject_tree(db: AsyncSession = Depends(get_db)):
    """取得 科目→年級 樹狀結構（選科目不選年級 = 涵蓋全年級）"""
    service = SubjectService(db)
    tree = await service.get_subject_tree()
    return SubjectTreeResponse(subjects=tree, total=len(tree))


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db)
):
    """取得單一科目"""
    service = SubjectService(db)
    subject = await service.get_subject_by_id(subject_id)
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"科目 ID {subject_id} 不存在"
        )
    
    return SubjectResponse.from_orm(subject)


@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject_data: SubjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """建立科目"""
    service = SubjectService(db)
    
    print(subject_data)
    try:
        subject = await service.create_subject(subject_data)
        return SubjectResponse.from_orm(subject)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新科目"""
    service = SubjectService(db)
    
    try:
        subject = await service.update_subject(subject_id, subject_data)
        
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"科目 ID {subject_id} 不存在"
            )
        
        return SubjectResponse.model_validate(subject)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{subject_id}")
async def delete_subject(
    subject_id: int,
    force: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """刪除科目"""
    service = SubjectService(db)
    
    try:
        success = await service.delete_subject(subject_id, force=force)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"科目 ID {subject_id} 不存在"
            )
        
        return {"message": f"科目已{'強制' if force else ''}刪除"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/usage/stats")
async def get_subject_usage_stats(db: AsyncSession = Depends(get_db)):
    """取得科目使用統計"""
    service = SubjectService(db)
    stats = await service.get_subject_usage_stats()
    
    return {"stats": stats}