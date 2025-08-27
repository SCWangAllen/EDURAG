import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import database
from app.schemas.question import (
    GenerateRequest, 
    GenerateResponse, 
    QuestionItem, 
    QuestionType,
    QuestionSource
)
from app.services.retrieval import search_similar_chunks
from app.core.llm_client import generate_questions_by_type

router = APIRouter(prefix="/api/generate", tags=["generate"])

@router.post("/", response_model=GenerateResponse)
async def generate(req: GenerateRequest, db: AsyncSession = Depends(database.get_db)):
    start_time = time.time()
    
    try:
        # 1. 檢索相關文本塊（為所有題型使用通用查詢）
        context_query = f"{req.subject.value} 題目 教材內容"
        chunks_with_scores = await search_similar_chunks(
            db=db,
            query=context_query,
            document_id=req.document_id,
            top_k=8,  # 取更多塊以支持多種題型
            similarity_threshold=0.1
        )
        
        if not chunks_with_scores:
            raise HTTPException(
                status_code=404,
                detail=f"文件 ID {req.document_id} 中找不到相關內容"
            )
        
        # 2. 準備內容給LLM
        context_texts = [chunk.slice_text for chunk, score in chunks_with_scores]
        context_str = "\n".join(f"{i+1}. {text}" for i, text in enumerate(context_texts[:5]))
        
        # 3. 按題型生成題目
        all_questions = []
        
        for question_type, count in req.types.items():
            if count > 0:
                # 為每種題型生成相應數量的題目
                questions = await generate_questions_by_type(
                    context=context_str,
                    question_type=question_type,
                    count=count,
                    subject=req.subject
                )
                
                # 轉換為 QuestionItem 格式
                for i, q in enumerate(questions):
                    # 為每個題目分配一個來源塊
                    chunk_idx = i % len(chunks_with_scores)
                    chunk, score = chunks_with_scores[chunk_idx]
                    
                    question_item = QuestionItem(
                        type=question_type,
                        prompt=q['prompt'],
                        options=q.get('options'),
                        answer=q['answer'],
                        explanation=q['explanation'],
                        source=QuestionSource(
                            document_id=req.document_id,
                            chunk_id=chunk.id,
                            chunk_text=chunk.slice_text[:200] + "..." if len(chunk.slice_text) > 200 else chunk.slice_text
                        )
                    )
                    all_questions.append(question_item)
        
        generation_time = time.time() - start_time
        
        return GenerateResponse(
            items=all_questions,
            total_count=len(all_questions),
            generation_time=generation_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"題目生成失敗: {str(e)}"
        )
