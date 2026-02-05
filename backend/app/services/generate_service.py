"""
題目生成 Service — 從 routers/generate.py 提取的業務邏輯。
"""
import time
import logging
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Template, Document
from app.core.config import RETRIEVAL_TOP_K, SIMILARITY_THRESHOLD
from app.schemas.question import (
    QuestionItem,
    QuestionType,
    QuestionSource,
    GenerateRequest,
    GenerateResponse,
    SingleGenerateRequest,
    SingleGenerateResponse,
    TemplateGenerateRequest,
    TemplateGenerateResponse,
    PromptGenerateRequest,
    PromptGenerateResponse,
    TemplateEnhancedGenerateRequest,
    TemplateEnhancedGenerateResponse,
)
from app.services.retrieval import search_similar_chunks
from app.core.llm_client import (
    generate_questions_by_type,
    generate_questions_by_template,
    detect_question_type_from_template,
    generate_questions_by_prompt,
)

logger = logging.getLogger(__name__)


class GenerateService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------ #
    #  基本生成（按科目 + 題型）
    # ------------------------------------------------------------------ #
    async def generate_basic(self, req: GenerateRequest) -> GenerateResponse:
        start_time = time.time()

        context_query = f"{req.subject.value} 題目 教材內容"
        chunks_with_scores = await search_similar_chunks(
            db=self.db,
            query=context_query,
            document_id=req.document_id,
            top_k=RETRIEVAL_TOP_K,
            similarity_threshold=SIMILARITY_THRESHOLD,
        )

        if not chunks_with_scores:
            raise ValueError(f"文件 ID {req.document_id} 中找不到相關內容")

        context_texts = [chunk.slice_text for chunk, score in chunks_with_scores]
        context_str = "\n".join(
            f"{i+1}. {text}" for i, text in enumerate(context_texts[:5])
        )

        all_questions: List[QuestionItem] = []

        for question_type, count in req.types.items():
            if count > 0:
                questions = await generate_questions_by_type(
                    context=context_str,
                    question_type=question_type,
                    count=count,
                    subject=req.subject,
                )

                for i, q in enumerate(questions):
                    chunk_idx = i % len(chunks_with_scores)
                    chunk, score = chunks_with_scores[chunk_idx]

                    question_item = QuestionItem(
                        type=question_type,
                        prompt=q["prompt"],
                        options=q.get("options"),
                        answer=q["answer"],
                        explanation=q["explanation"],
                        source=QuestionSource(
                            document_id=req.document_id,
                            chunk_id=chunk.id,
                            chunk_text=(
                                chunk.slice_text[:200] + "..."
                                if len(chunk.slice_text) > 200
                                else chunk.slice_text
                            ),
                        ),
                    )
                    all_questions.append(question_item)

        generation_time = time.time() - start_time

        return GenerateResponse(
            items=all_questions,
            total_count=len(all_questions),
            generation_time=generation_time,
        )

    # ------------------------------------------------------------------ #
    #  單一生成（模板 + 向量搜索）
    # ------------------------------------------------------------------ #
    async def generate_single(
        self, gen_req: SingleGenerateRequest
    ) -> SingleGenerateResponse:
        start_time = time.time()

        template = await self._get_template(gen_req.template_id)

        all_contexts: List[tuple] = []
        for doc_id in gen_req.document_ids:
            context_query = f"{gen_req.question_type.value} 題目 教材內容"
            chunks_with_scores = await search_similar_chunks(
                db=self.db,
                query=context_query,
                document_id=doc_id,
                top_k=5,
                similarity_threshold=SIMILARITY_THRESHOLD,
            )
            if chunks_with_scores:
                all_contexts.extend(
                    [(doc_id, chunk, score) for chunk, score in chunks_with_scores]
                )

        if not all_contexts:
            raise ValueError("在指定文件中找不到相關內容")

        combined_context = "\n".join(
            [chunk.slice_text for _, chunk, _ in all_contexts[:8]]
        )
        full_prompt = template.content.replace("{{context}}", combined_context)

        questions = await generate_questions_by_type(
            context=full_prompt,
            question_type=gen_req.question_type,
            count=gen_req.count,
            subject=None,
        )

        question_items = self._build_question_items_from_contexts(
            questions, gen_req.question_type, all_contexts
        )

        generation_time = time.time() - start_time

        return SingleGenerateResponse(
            question_type=gen_req.question_type,
            template_id=gen_req.template_id,
            items=question_items,
            count=len(question_items),
            generation_time=generation_time,
        )

    # ------------------------------------------------------------------ #
    #  模板生成（直接文件內容，不使用向量搜索）
    # ------------------------------------------------------------------ #
    async def generate_from_template(
        self, gen_req: TemplateGenerateRequest
    ) -> TemplateGenerateResponse:
        start_time = time.time()

        logger.info(
            "開始模板生成請求 - Template ID: %s, Document IDs: %s, Count: %s",
            gen_req.template_id,
            gen_req.document_ids,
            gen_req.count,
        )

        template = await self._get_template(gen_req.template_id)

        logger.info("找到模板 - Name: %s, Subject: %s", template.name, template.subject)

        detected_types = detect_question_type_from_template(template.content)
        logger.info("檢測到的題型: %s", detected_types)

        documents_content = await self._load_documents(gen_req.document_ids)

        if not documents_content:
            raise ValueError("找不到指定的文件")

        combined_context = "\n\n".join(
            [
                f"文件: {doc['title']}\n內容: {doc['content']}"
                for doc in documents_content
            ]
        )

        logger.info("合併後的內容長度: %d 字符", len(combined_context))

        questions = await generate_questions_by_template(
            context=combined_context,
            template_content=template.content,
            count=gen_req.count,
        )
        logger.info("Claude API 回應完成，收到 %d 道題目", len(questions))

        question_items = self._build_question_items_from_docs(
            questions, QuestionType.AUTO, documents_content
        )

        generation_time = time.time() - start_time

        logger.info(
            "模板生成完成！總耗時: %.2f秒, 生成題目數: %d",
            generation_time,
            len(question_items),
        )

        return TemplateGenerateResponse(
            template_id=gen_req.template_id,
            template_name=template.name,
            detected_question_types=detected_types,
            items=question_items,
            count=len(question_items),
            generation_time=generation_time,
        )

    # ------------------------------------------------------------------ #
    #  Prompt 生成（前端自由 prompt）
    # ------------------------------------------------------------------ #
    async def generate_from_prompt(
        self, req: PromptGenerateRequest
    ) -> PromptGenerateResponse:
        start_time = time.time()

        logger.info("收到 Prompt 生成請求, Prompt 長度: %d 字符", len(req.prompt))

        questions = await generate_questions_by_prompt(
            prompt=req.prompt,
            count=req.count,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            model=req.model,
            question_type=req.question_type,
        )

        question_items: List[QuestionItem] = []
        for q in questions:
            question_item = QuestionItem(
                type=req.question_type or QuestionType.AUTO,
                prompt=q["prompt"],
                options=q.get("options"),
                answer=q["answer"],
                explanation=q["explanation"],
                source=QuestionSource(
                    document_id=0,
                    chunk_id=0,
                    chunk_text="前端提供的 prompt 生成",
                ),
            )
            question_items.append(question_item)

        generation_time = time.time() - start_time
        logger.info(
            "Prompt 生成完成！總耗時: %.2f秒, 生成題目數: %d",
            generation_time,
            len(question_items),
        )

        return PromptGenerateResponse(
            prompt=(
                req.prompt[:200] + "..." if len(req.prompt) > 200 else req.prompt
            ),
            detected_question_type=req.question_type,
            items=question_items,
            count=len(question_items),
            generation_time=generation_time,
            model_used=req.model,
            tokens_used=None,
        )

    # ------------------------------------------------------------------ #
    #  增強模板生成（前端傳入完整模板資訊 + 文件內容）
    # ------------------------------------------------------------------ #
    async def generate_template_enhanced(
        self, req: TemplateEnhancedGenerateRequest
    ) -> TemplateEnhancedGenerateResponse:
        start_time = time.time()

        template = req.template
        template_content = template.get("content", "")
        template_params = template.get("params", {})

        actual_temperature = template_params.get(
            "temperature", req.temperature or 0.7
        )
        actual_max_tokens = template_params.get(
            "max_tokens", req.max_tokens or 2000
        )
        actual_top_p = template_params.get("top_p", 1.0)
        actual_frequency_penalty = template_params.get("frequency_penalty", 0.0)

        logger.info(
            "使用參數 - Temperature: %s, Max tokens: %s, Top P: %s",
            actual_temperature,
            actual_max_tokens,
            actual_top_p,
        )

        documents_content: List[str] = []
        for doc in req.documents:
            doc_content = f"=== {doc.get('title', 'Unknown')} ===\n"
            if doc.get("chapter"):
                doc_content += f"章節: {doc['chapter']}\n"
            doc_content += doc.get("content", "")
            documents_content.append(doc_content)

        combined_content = "\n\n".join(documents_content)

        full_prompt = template_content.replace("{context}", combined_content)

        template_question_type = (
            template.get("question_type") or req.question_type or "single_choice"
        )
        logger.info("使用題型: %s", template_question_type)

        questions = await generate_questions_by_prompt(
            prompt=full_prompt,
            count=req.count,
            temperature=actual_temperature,
            max_tokens=actual_max_tokens,
            model=req.model,
            question_type=template_question_type,
            top_p=actual_top_p,
            frequency_penalty=actual_frequency_penalty,
        )

        is_fallback = False
        warning_message = None

        if not questions:
            is_fallback = True
            warning_message = (
                "LLM 無法從提供的文件內容生成有效題目。可能原因：\n"
                "1. 文件內容與題型不符\n"
                "2. 文件內容過短或不完整\n"
                "3. LLM API 暫時無法正常回應\n\n"
                "建議：\n"
                "- 檢查選擇的文件是否包含足夠的教材內容\n"
                "- 嘗試選擇不同的文件或題型\n"
                "- 調整模板的 Prompt 描述"
            )
            logger.error("LLM 生成失敗，返回空列表")
        elif len(questions) < req.count:
            warning_message = (
                f"請求生成 {req.count} 題，但只成功生成 {len(questions)} 題。\n\n"
                "可能原因：\n"
                "- 文件內容不足以支撐請求的題目數量\n"
                "- 部分生成的題目格式驗證失敗\n\n"
                "建議：請嘗試減少生成數量或選擇更多文件。"
            )
            logger.warning(warning_message)

        question_items: List[QuestionItem] = []
        for i, q in enumerate(questions):
            source = QuestionSource(
                document_id=req.documents[0].get("id", 1) if req.documents else 1,
                chunk_id=1,
                chunk_text=(
                    combined_content[:200] + "..."
                    if len(combined_content) > 200
                    else combined_content
                ),
            )

            question_item = QuestionItem(
                type=getattr(
                    QuestionType, template_question_type.upper(), QuestionType.AUTO
                ),
                prompt=q["prompt"],
                options=q.get("options"),
                answer=q["answer"],
                explanation=q.get("explanation", ""),
                source=source,
            )
            question_items.append(question_item)

        generation_time = time.time() - start_time
        logger.info(
            "模板生成完成，耗時 %.2f 秒，生成 %d 道題目",
            generation_time,
            len(question_items),
        )

        params_used = {
            "temperature": actual_temperature,
            "max_tokens": actual_max_tokens,
            "top_p": actual_top_p,
            "frequency_penalty": actual_frequency_penalty,
            "model": req.model,
        }

        return TemplateEnhancedGenerateResponse(
            template_info={
                "id": template.get("id"),
                "name": template.get("name"),
                "subject": template.get("subject"),
                "content_preview": (
                    template_content[:200] + "..."
                    if len(template_content) > 200
                    else template_content
                ),
            },
            documents_info=[
                {
                    "id": doc.get("id"),
                    "title": doc.get("title"),
                    "content_length": len(doc.get("content", "")),
                }
                for doc in req.documents
            ],
            detected_question_type=template_question_type,
            items=question_items,
            count=len(question_items),
            generation_time=generation_time,
            model_used=req.model,
            params_used=params_used,
            warning=warning_message,
            is_fallback=is_fallback,
        )

    # ------------------------------------------------------------------ #
    #  Private helpers
    # ------------------------------------------------------------------ #
    async def _get_template(self, template_id: int) -> Template:
        template_query = select(Template).where(Template.id == template_id)
        template_result = await self.db.execute(template_query)
        template = template_result.scalar_one_or_none()
        if not template:
            raise ValueError(f"模板 ID {template_id} 不存在")
        return template

    async def _load_documents(
        self, document_ids: List[int]
    ) -> List[Dict[str, Any]]:
        documents_content: List[Dict[str, Any]] = []
        for doc_id in document_ids:
            doc_query = select(Document).where(Document.id == doc_id)
            doc_result = await self.db.execute(doc_query)
            document = doc_result.scalar_one_or_none()
            if document:
                logger.info(
                    "找到文件 - Title: %s, Content length: %d 字符",
                    document.title,
                    len(document.content),
                )
                documents_content.append(
                    {
                        "id": document.id,
                        "title": document.title,
                        "content": document.content,
                    }
                )
            else:
                logger.warning("文件不存在 - Document ID: %d", doc_id)
        return documents_content

    @staticmethod
    def _build_question_items_from_contexts(
        questions: List[Dict[str, Any]],
        question_type: QuestionType,
        all_contexts: List[tuple],
    ) -> List[QuestionItem]:
        question_items: List[QuestionItem] = []
        for i, q in enumerate(questions):
            context_idx = i % len(all_contexts)
            doc_id, chunk, _ = all_contexts[context_idx]

            question_item = QuestionItem(
                type=question_type,
                prompt=q["prompt"],
                options=q.get("options"),
                answer=q["answer"],
                explanation=q["explanation"],
                source=QuestionSource(
                    document_id=doc_id,
                    chunk_id=chunk.id,
                    chunk_text=(
                        chunk.slice_text[:200] + "..."
                        if len(chunk.slice_text) > 200
                        else chunk.slice_text
                    ),
                ),
            )
            question_items.append(question_item)
        return question_items

    @staticmethod
    def _build_question_items_from_docs(
        questions: List[Dict[str, Any]],
        question_type: QuestionType,
        documents_content: List[Dict[str, Any]],
    ) -> List[QuestionItem]:
        question_items: List[QuestionItem] = []
        for i, q in enumerate(questions):
            doc_idx = i % len(documents_content)
            source_doc = documents_content[doc_idx]

            question_item = QuestionItem(
                type=question_type,
                prompt=q["prompt"],
                options=q.get("options"),
                answer=q["answer"],
                explanation=q["explanation"],
                source=QuestionSource(
                    document_id=source_doc["id"],
                    chunk_id=0,
                    chunk_text=(
                        source_doc["content"][:200] + "..."
                        if len(source_doc["content"]) > 200
                        else source_doc["content"]
                    ),
                ),
            )
            question_items.append(question_item)
        return question_items
