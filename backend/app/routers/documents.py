from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.document_service import DocumentService, MockDocumentService
from app.core.config import USE_MOCK_API
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_document_service(db: AsyncSession = Depends(get_db)) -> DocumentService:
    """獲取文件服務實例"""
    if USE_MOCK_API:
        return MockDocumentService()
    return DocumentService(db)


@router.get("/", response_model=Dict[str, Any])
async def get_documents(
    subject: Optional[str] = Query(None, description="科目篩選"),
    grade: Optional[str] = Query(None, description="年級篩選 (G1-G6, ALL)"),
    chapter: Optional[str] = Query(None, description="章節篩選"),
    search: Optional[str] = Query(None, description="搜尋關鍵字"),
    page: int = Query(1, ge=1, description="頁碼"),
    size: int = Query(20, ge=1, le=100, description="每頁數量"),
    service: DocumentService = Depends(get_document_service)
):
    """取得文件清單"""
    try:
        skip = (page - 1) * size
        result = await service.get_documents(
            subject=subject,
            grade=grade,
            chapter=chapter,
            search_query=search,
            skip=skip,
            limit=size
        )

        logger.info(f"Retrieved {len(result['documents'])} documents (total: {result['total']}, grade: {grade})")
        return result

    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=Dict[str, Any])
async def get_document_stats(
    service: DocumentService = Depends(get_document_service)
):
    """取得文件統計"""
    try:
        stats = await service.get_document_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting document stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subjects", response_model=Dict[str, Any])
async def get_subjects(
    service: DocumentService = Depends(get_document_service)
):
    """取得所有科目清單"""
    try:
        if USE_MOCK_API:
            # Mock 模式回傳固定科目
            subjects = ['Health']
        else:
            subjects = await service.get_subjects()
            
        return {'subjects': subjects}
        
    except Exception as e:
        logger.error(f"Error getting subjects: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=Dict[str, Any])
async def search_documents(
    q: str = Query(..., description="搜尋關鍵字"),
    subject: Optional[str] = Query(None, description="科目篩選"),
    grade: Optional[str] = Query(None, description="年級篩選"),
    limit: int = Query(10, ge=1, le=50, description="結果數量"),
    service: DocumentService = Depends(get_document_service)
):
    """搜尋文件"""
    try:
        if USE_MOCK_API:
            # Mock 模式使用簡化的搜尋
            result = await service.get_documents(
                subject=subject,
                grade=grade,
                search_query=q,
                skip=0,
                limit=limit
            )
            return {
                'documents': result['documents'],
                'total': result['total']
            }
        else:
            # 真實模式使用進階搜尋
            documents = await service.search_documents(q, subject, grade, limit)
            return {
                'documents': documents,
                'total': len(documents)
            }

    except Exception as e:
        logger.error(f"Error searching documents with query '{q}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}", response_model=Dict[str, Any])
async def get_document(
    document_id: int,
    service: DocumentService = Depends(get_document_service)
):
    """取得單一文件詳情"""
    try:
        document = await service.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="文件不存在")
            
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/chapters", response_model=Dict[str, Any])
async def get_document_chapters(
    document_id: int,
    service: DocumentService = Depends(get_document_service)
):
    """取得文件的章節清單"""
    try:
        # 先確認文件存在
        document = await service.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 如果是 Mock 模式
        if USE_MOCK_API:
            return {
                'chapters': [f'Chapter {i}' for i in range(1, 16)]
            }
        
        # 真實模式：取得該科目的所有章節
        subject = document['subject']
        if hasattr(service, 'get_chapters_by_subject'):
            chapters = await service.get_chapters_by_subject(subject)
        else:
            chapters = []
            
        return {'chapters': chapters}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chapters for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{document_id}", response_model=Dict[str, Any])
async def update_document(
    document_id: int,
    update_data: Dict[str, Any],
    service: DocumentService = Depends(get_document_service)
):
    """更新文件"""
    try:
        updated_document = await service.update_document(document_id, update_data)
        if not updated_document:
            raise HTTPException(status_code=404, detail="文件不存在")
            
        return updated_document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/references", response_model=Dict[str, Any])
async def check_document_references(
    document_id: int,
    service: DocumentService = Depends(get_document_service)
):
    """檢查文件是否被其他資料引用"""
    try:
        if USE_MOCK_API:
            # Mock 模式回傳假資料
            return {
                'questions': 0,
                'embeddings': 0,
                'has_references': False
            }
            
        references = await service.check_document_references(document_id)
        return references
        
    except Exception as e:
        logger.error(f"Error checking references for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}", response_model=Dict[str, Any])
async def delete_document(
    document_id: int,
    force: bool = Query(False, description="是否強制刪除（同時刪除相關問題）"),
    service: DocumentService = Depends(get_document_service)
):
    """刪除文件"""
    try:
        if USE_MOCK_API:
            # Mock 模式直接成功
            return {
                "success": True,
                "message": "文件已刪除 (Mock模式)",
                "document_id": document_id,
                "deleted_references": {"questions": 0, "embeddings": 0}
            }
            
        result = await service.delete_document(document_id, force=force)
        
        if not result['success']:
            if result['error_type'] == 'not_found':
                raise HTTPException(status_code=404, detail="文件不存在")
            elif result['error_type'] == 'has_references':
                # 回傳引用資訊，讓前端決定是否強制刪除
                raise HTTPException(
                    status_code=409,  # Conflict
                    detail={
                        "message": "文件正被其他資料引用，無法直接刪除",
                        "references": result['references'],
                        "can_force_delete": True
                    }
                )
            else:
                raise HTTPException(status_code=500, detail=result['error'])
        
        return {
            "success": True,
            "message": "文件已刪除" + ("（包含相關問題）" if force else ""),
            "document_id": document_id,
            "deleted_references": result['deleted_references']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))