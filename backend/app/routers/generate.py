import time
import asyncio
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import database
from app.db.models import Template, Document

# 設置日志記錄器
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
from app.schemas.question import (
    GenerateRequest, 
    GenerateResponse, 
    BatchGenerateRequest,
    BatchGenerateResponse,
    SingleGenerateRequest,
    SingleGenerateResponse,
    TemplateGenerateRequest,
    TemplateGenerateResponse,
    BatchTemplateGenerateRequest,
    BatchTemplateGenerateResponse,
    PromptGenerateRequest,
    PromptGenerateResponse,
    QuestionItem, 
    QuestionType,
    QuestionSource
)
from app.services.retrieval import search_similar_chunks
from app.core.llm_client import generate_questions_by_type, generate_questions_by_template, detect_question_type_from_template, generate_questions_by_prompt

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

async def _generate_single(gen_req: SingleGenerateRequest, db: AsyncSession) -> SingleGenerateResponse:
    """處理單一生成請求"""
    start_time = time.time()
    
    try:
        # 1. 查詢模板
        template_query = select(Template).where(Template.id == gen_req.template_id)
        template_result = await db.execute(template_query)
        template = template_result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(
                status_code=404,
                detail=f"模板 ID {gen_req.template_id} 不存在"
            )
        
        # 2. 為每個文件檢索相關內容
        all_contexts = []
        for doc_id in gen_req.document_ids:
            context_query = f"{gen_req.question_type.value} 題目 教材內容"
            chunks_with_scores = await search_similar_chunks(
                db=db,
                query=context_query,
                document_id=doc_id,
                top_k=5,
                similarity_threshold=0.1
            )
            
            if chunks_with_scores:
                all_contexts.extend([(doc_id, chunk, score) for chunk, score in chunks_with_scores])
        
        if not all_contexts:
            raise HTTPException(
                status_code=404,
                detail=f"在指定文件中找不到相關內容"
            )
        
        # 3. 準備完整的模板內容給LLM
        combined_context = "\n".join([chunk.slice_text for _, chunk, _ in all_contexts[:8]])
        full_prompt = template.content.replace("{{context}}", combined_context)
        
        # 4. 生成題目
        questions = await generate_questions_by_type(
            context=full_prompt,
            question_type=gen_req.question_type,
            count=gen_req.count,
            subject=None  # 使用模板而不是subject
        )
        
        # 5. 轉換為 QuestionItem 格式
        question_items = []
        for i, q in enumerate(questions):
            # 為每個題目分配一個來源塊
            context_idx = i % len(all_contexts)
            doc_id, chunk, _ = all_contexts[context_idx]
            
            question_item = QuestionItem(
                type=gen_req.question_type,
                prompt=q['prompt'],
                options=q.get('options'),
                answer=q['answer'],
                explanation=q['explanation'],
                source=QuestionSource(
                    document_id=doc_id,
                    chunk_id=chunk.id,
                    chunk_text=chunk.slice_text[:200] + "..." if len(chunk.slice_text) > 200 else chunk.slice_text
                )
            )
            question_items.append(question_item)
        
        generation_time = time.time() - start_time
        
        return SingleGenerateResponse(
            question_type=gen_req.question_type,
            template_id=gen_req.template_id,
            items=question_items,
            count=len(question_items),
            generation_time=generation_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成題目失敗: {str(e)}"
        )

@router.post("/batch", response_model=BatchGenerateResponse)
async def generate_batch(req: BatchGenerateRequest, db: AsyncSession = Depends(database.get_db)):
    """批次生成題目"""
    start_time = time.time()
    
    results = []
    errors = []
    success_count = 0
    total_items = 0
    
    # 並行處理所有生成請求
    tasks = [_generate_single(gen_req, db) for gen_req in req.generations]
    
    try:
        # 使用 asyncio.gather 並行執行，允許部分失敗
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(task_results):
            if isinstance(result, Exception):
                error_msg = f"請求 {i+1} 失敗: {str(result)}"
                errors.append(error_msg)
            else:
                results.append(result)
                success_count += 1
                total_items += result.count
        
    except Exception as e:
        errors.append(f"批次處理失敗: {str(e)}")
    
    total_time = time.time() - start_time
    
    return BatchGenerateResponse(
        results=results,
        total_items=total_items,
        total_time=total_time,
        success_count=success_count,
        error_count=len(errors),
        errors=errors
    )

async def _generate_template(gen_req: TemplateGenerateRequest, db: AsyncSession) -> TemplateGenerateResponse:
    """處理模板驅動的生成請求"""
    start_time = time.time()
    
    logger.info(f"🚀 開始模板生成請求 - Template ID: {gen_req.template_id}, Document IDs: {gen_req.document_ids}, Count: {gen_req.count}")
    
    try:
        # 1. 查詢模板
        template_query = select(Template).where(Template.id == gen_req.template_id)
        template_result = await db.execute(template_query)
        template = template_result.scalar_one_or_none()
        
        if not template:
            logger.error(f"❌ 模板不存在 - Template ID: {gen_req.template_id}")
            raise HTTPException(
                status_code=404,
                detail=f"模板 ID {gen_req.template_id} 不存在"
            )
        
        logger.info(f"📝 找到模板 - Name: {template.name}, Subject: {template.subject}")
        logger.info(f"📄 模板內容: {template.content[:200]}...")
        
        # 2. 檢測模板的題型
        detected_types = detect_question_type_from_template(template.content)
        logger.info(f"🎯 檢測到的題型: {detected_types}")
        
        # 3. 直接查詢文件內容（不使用向量搜索）
        documents_content = []
        for doc_id in gen_req.document_ids:
            logger.info(f"🔍 查詢文件 - Document ID: {doc_id}")
            doc_query = select(Document).where(Document.id == doc_id)
            doc_result = await db.execute(doc_query)
            document = doc_result.scalar_one_or_none()
            
            if document:
                logger.info(f"📄 找到文件 - Title: {document.title}, Content length: {len(document.content)} 字符")
                logger.info(f"📄 文件內容預覽: {document.content[:200]}...")
                documents_content.append({
                    'id': document.id,
                    'title': document.title,
                    'content': document.content
                })
            else:
                logger.warning(f"⚠️ 文件不存在 - Document ID: {doc_id}")
        
        if not documents_content:
            logger.error(f"❌ 沒有找到任何指定的文件")
            raise HTTPException(
                status_code=404,
                detail="找不到指定的文件"
            )
        
        # 4. 合併文件內容
        combined_context = "\n\n".join([
            f"文件: {doc['title']}\n內容: {doc['content']}" 
            for doc in documents_content
        ])
        
        logger.info(f"📝 合併後的內容長度: {len(combined_context)} 字符")
        logger.info(f"📝 合併內容預覽: {combined_context[:300]}...")
        
        logger.info(f"🤖 開始呼叫 Claude API 生成題目...")
        questions = await generate_questions_by_template(
            context=combined_context,
            template_content=template.content,
            count=gen_req.count
        )
        logger.info(f"✅ Claude API 回應完成，收到 {len(questions)} 道題目")
        
        # 5. 轉換為 QuestionItem 格式
        question_items = []
        for i, q in enumerate(questions):
            logger.info(f"📝 處理題目 {i+1}: {q.get('prompt', '')[:100]}...")
            
            # 循環分配文件作為來源
            doc_idx = i % len(documents_content)
            source_doc = documents_content[doc_idx]
            
            question_item = QuestionItem(
                type=QuestionType.AUTO,  # 由模板自動決定
                prompt=q['prompt'],
                options=q.get('options'),
                answer=q['answer'],
                explanation=q['explanation'],
                source=QuestionSource(
                    document_id=source_doc['id'],
                    chunk_id=0,  # 不使用 chunk，設為 0
                    chunk_text=source_doc['content'][:200] + "..." if len(source_doc['content']) > 200 else source_doc['content']
                )
            )
            question_items.append(question_item)
        
        generation_time = time.time() - start_time
        
        logger.info(f"🎉 模板生成完成！總耗時: {generation_time:.2f}秒, 生成題目數: {len(question_items)}")
        
        return TemplateGenerateResponse(
            template_id=gen_req.template_id,
            template_name=template.name,
            detected_question_types=detected_types,
            items=question_items,
            count=len(question_items),
            generation_time=generation_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 模板生成失敗: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"模板生成失敗: {str(e)}"
        )

@router.post("/template", response_model=TemplateGenerateResponse)
async def generate_template(req: TemplateGenerateRequest, db: AsyncSession = Depends(database.get_db)):
    """基於模板的題目生成"""
    logger.info(f"📡 收到單一模板生成請求: {req}")
    result = await _generate_template(req, db)
    logger.info(f"📡 單一模板生成回應完成")
    return result

@router.post("/template/batch", response_model=BatchTemplateGenerateResponse)
async def generate_template_batch(req: BatchTemplateGenerateRequest, db: AsyncSession = Depends(database.get_db)):
    """批次模板驅動生成"""
    start_time = time.time()
    
    logger.info(f"📡 收到批次模板生成請求，包含 {len(req.generations)} 個生成任務")
    for i, gen_req in enumerate(req.generations):
        logger.info(f"📡 任務 {i+1}: Template ID: {gen_req.template_id}, Document IDs: {gen_req.document_ids}, Count: {gen_req.count}")
    
    results = []
    errors = []
    success_count = 0
    total_items = 0
    
    # 並行處理所有模板生成請求
    tasks = [_generate_template(gen_req, db) for gen_req in req.generations]
    
    try:
        # 使用 asyncio.gather 並行執行，允許部分失敗
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(task_results):
            if isinstance(result, Exception):
                error_msg = f"請求 {i+1} 失敗: {str(result)}"
                logger.error(f"❌ {error_msg}")
                errors.append(error_msg)
            else:
                logger.info(f"✅ 任務 {i+1} 成功，生成了 {result.count} 道題目")
                results.append(result)
                success_count += 1
                total_items += result.count
        
    except Exception as e:
        error_msg = f"批次處理失敗: {str(e)}"
        logger.error(f"❌ {error_msg}")
        errors.append(error_msg)
    
    total_time = time.time() - start_time
    
    logger.info(f"🎉 批次模板生成完成！成功: {success_count}, 失敗: {len(errors)}, 總題目數: {total_items}, 總耗時: {total_time:.2f}秒")
    
    return BatchTemplateGenerateResponse(
        results=results,
        total_items=total_items,
        total_time=total_time,
        success_count=success_count,
        error_count=len(errors),
        errors=errors
    )

@router.post("/prompt", response_model=PromptGenerateResponse)
async def generate_prompt(req: PromptGenerateRequest):
    """基於前端提供的完整 prompt 生成題目"""
    start_time = time.time()
    
    logger.info(f"📡 收到 Prompt 生成請求")
    logger.info(f"📝 Prompt 長度: {len(req.prompt)} 字符, Count: {req.count}")
    logger.info(f"📝 參數 - Temperature: {req.temperature}, Max tokens: {req.max_tokens}, Model: {req.model}")
    
    try:
        # 直接使用前端提供的 prompt
        questions = await generate_questions_by_prompt(
            prompt=req.prompt,
            count=req.count,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            model=req.model,
            question_type=req.question_type
        )
        
        # 轉換為 QuestionItem 格式
        question_items = []
        for i, q in enumerate(questions):
            logger.info(f"📝 處理 Prompt 生成題目 {i+1}: {q.get('prompt', '')[:100]}...")
            
            question_item = QuestionItem(
                type=req.question_type or QuestionType.AUTO,
                prompt=q['prompt'],
                options=q.get('options'),
                answer=q['answer'],
                explanation=q['explanation'],
                source=QuestionSource(
                    document_id=0,  # 前端驅動，不指定特定文件
                    chunk_id=0,
                    chunk_text="前端提供的 prompt 生成"
                )
            )
            question_items.append(question_item)
        
        generation_time = time.time() - start_time
        
        logger.info(f"🎉 Prompt 生成完成！總耗時: {generation_time:.2f}秒, 生成題目數: {len(question_items)}")
        
        return PromptGenerateResponse(
            prompt=req.prompt[:200] + "..." if len(req.prompt) > 200 else req.prompt,
            detected_question_type=req.question_type,
            items=question_items,
            count=len(question_items),
            generation_time=generation_time,
            model_used=req.model,
            tokens_used=None  # Claude API 不返回 token 使用量
        )
        
    except Exception as e:
        logger.error(f"❌ Prompt 生成失敗: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Prompt 生成失敗: {str(e)}"
        )
