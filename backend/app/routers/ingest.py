import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import models, database
from app.schemas.ingest import IngestRequest, IngestResponse, ChunkInfo
from app.core.embeddings import create_embedding

router = APIRouter(prefix="/api/ingest", tags=["ingest"])

def smart_text_chunking(text: str, max_chunk_size: int = 300, overlap_size: int = 50) -> List[str]:
    """智能文本分塊，優於簡單句號分割"""
    # 先按句號分割
    sentences = [s.strip() for s in text.split("。") if s.strip()]
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # 如果當前塊加上新句子不超過最大長度，就添加
        if len(current_chunk + sentence) <= max_chunk_size:
            current_chunk = current_chunk + sentence + "。" if current_chunk else sentence + "。"
        else:
            # 否則儲存當前塊並開始新塊
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + "。"
    
    # 添加最後一塊
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

@router.post("/", response_model=IngestResponse)
async def ingest(request: IngestRequest, db: AsyncSession = Depends(database.get_db)):
    start_time = time.time()
    
    try:
        # 1. 儲存文件
        doc = models.Document(
            subject=request.subject.value,
            content=request.text,
            title=request.title
        )
        db.add(doc)
        await db.flush()  # 取得 doc.id
        
        # 2. 智能文本分塊
        chunks_text = smart_text_chunking(request.text)
        
        if not chunks_text:
            raise HTTPException(
                status_code=400,
                detail="文本內容無法分塊處理"
            )
        
        # 3. 為每個塊生成embedding並存入資料庫
        chunk_infos = []
        for i, chunk_text in enumerate(chunks_text):
            try:
                # 生成向量
                vector = await create_embedding(chunk_text)
                
                # 儲存 embedding
                embedding = models.Embedding(
                    document_id=doc.id,
                    slice_text=chunk_text,
                    vector=vector
                )
                db.add(embedding)
                await db.flush()  # 取得 embedding.id
                
                # 建立回傳資訊
                chunk_info = ChunkInfo(
                    chunk_id=embedding.id,
                    text=chunk_text,
                    token_count=len(chunk_text)  # 簡單的字元計數
                )
                chunk_infos.append(chunk_info)
                
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"處理文本塊 {i+1} 時發生錯誤: {str(e)}"
                )
        
        await db.commit()
        processing_time = time.time() - start_time
        
        return IngestResponse(
            document_id=doc.id,
            chunks=chunk_infos,
            total_chunks=len(chunk_infos),
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"文件處理失敗: {str(e)}"
        )
