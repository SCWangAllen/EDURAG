from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.embeddings import create_embedding
from app.db.models import Embedding

async def search_similar_chunks(
    db: AsyncSession,
    query: str,
    document_id: int,
    top_k: int = 5,
    similarity_threshold: float = 0.1
) -> List[Tuple[Embedding, float]]:
    """
    使用向量相似度搜索相關文本塊
    
    Args:
        db: 資料庫會話
        query: 查詢文本
        document_id: 文件ID
        top_k: 返回結果數量
        similarity_threshold: 相似度閾值
        
    Returns:
        List of (embedding, similarity_score) tuples
    """
    # 生成查詢向量
    query_vector = await create_embedding(query)
    
    # 構建相似度搜索查詢
    # 使用餘弦相似度: 1 - (vector <=> query_vector)
    sql = text("""
        SELECT 
            id,
            document_id,
            slice_text,
            vector,
            created_at,
            (1 - (vector <=> :query_vector)) as similarity
        FROM embeddings 
        WHERE document_id = :document_id
        AND (1 - (vector <=> :query_vector)) > :threshold
        ORDER BY similarity DESC
        LIMIT :limit
    """)
    
    result = await db.execute(sql, {
        "query_vector": query_vector,
        "document_id": document_id,
        "threshold": similarity_threshold,
        "limit": top_k
    })
    
    rows = result.fetchall()
    
    # 轉換為 (Embedding, similarity) 元組
    embeddings_with_scores = []
    for row in rows:
        embedding = Embedding(
            id=row.id,
            document_id=row.document_id,
            slice_text=row.slice_text,
            vector=row.vector,
            created_at=row.created_at
        )
        embeddings_with_scores.append((embedding, row.similarity))
    
    return embeddings_with_scores

async def search_by_document_only(
    db: AsyncSession,
    document_id: int,
    limit: int = 5
) -> List[Embedding]:
    """
    簡單的文件內搜索（作為 fallback）
    """
    from sqlalchemy import select
    
    stmt = select(Embedding).where(
        Embedding.document_id == document_id
    ).limit(limit)
    
    result = await db.execute(stmt)
    return result.scalars().all()