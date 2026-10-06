from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, literal_column
from app.db.models import Question, Document
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse, QuestionListResponse, QuestionStatsResponse
from app.core.question_validation import QuestionValidationError, normalize_question_payload
from app.core.page_range import page_range_conditions, parse_page_range
from app.core.subject_norm import grade_sort_key
from app.services.document_service import chapter_sort_key, merge_all_grade_counts
import json
import csv
from io import StringIO
import pandas as pd
from datetime import datetime


def _metadata_field(name: str):
    """source_metadata JSON 欄位存取（->>），避免每處手刻 literal_column。"""
    return Question.source_metadata.op('->>')(literal_column(f"'{name}'"))


def question_facet_conditions(
    exclude: str,
    subject: Optional[str] = None,
    grade: Optional[str] = None,
    question_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    chapter: Optional[str] = None,
    page_from: Optional[int] = None,
    page_to: Optional[int] = None,
) -> list:
    """Facets 查詢用的篩選條件（純函式，可直接編譯 SQL 做測試）。

    與問題列表的篩選語意一致，但排除 `exclude` 指定的維度本身。
    page_from / page_to 依來源文件的課本頁碼篩選（呼叫端要 outer join documents）。
    """
    conditions = []
    if subject and exclude != 'subject':
        conditions.append(_metadata_field('subject') == subject)
    if grade and exclude != 'grade':
        grade_col = _metadata_field('grade')
        conditions.append(or_(grade_col == grade, grade_col == 'ALL'))
    if question_type and exclude != 'question_type':
        conditions.append(Question.question_type == question_type)
    if difficulty and exclude != 'difficulty':
        conditions.append(_metadata_field('difficulty') == difficulty)
    if chapter and exclude != 'chapter':
        conditions.append(_metadata_field('chapter') == chapter)
    conditions.extend(page_range_conditions(Document.page_number, page_from, page_to))
    return conditions


class QuestionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_response(self, question: Question, source_page: Optional[str] = None) -> QuestionResponse:
        """將資料庫 Question 模型轉換為 QuestionResponse schema

        source_page：來源文件（documents.page_number）的課本頁碼，由呼叫端
        join documents 後傳入；未 join 時維持 None，不影響其他欄位。
        """
        metadata = question.source_metadata or {}
        return QuestionResponse(
            id=question.id,
            type=question.question_type,
            content=question.stem,
            options=question.options,
            correct_answer=question.answer,
            explanation=question.explanation or '',
            source_document_id=question.document_id,
            source_content=metadata.get('source_content'),
            source_page=source_page,
            subject=metadata.get('subject'),
            chapter=metadata.get('chapter'),
            grade=metadata.get('grade'),
            difficulty=metadata.get('difficulty', 'medium'),
            question_data=question.question_data,  # 配對題的 left_items/right_items
            created_at=question.created_at,
            updated_at=question.updated_at
        )

    async def create_question(self, question_data: QuestionCreate) -> QuestionResponse:
        """創建新問題"""
        # 映射欄位名稱以符合資料庫模型
        data = question_data.model_dump()
        question = Question(
            question_type=data.get('type'),
            stem=data.get('content'),
            options=data.get('options'),
            answer=data.get('correct_answer'),
            explanation=data.get('explanation'),
            document_id=data.get('source_document_id'),
            question_data=data.get('question_data'),  # 配對題的 left_items/right_items
            source_metadata={
                'subject': data.get('subject'),
                'grade': data.get('grade'),
                'chapter': data.get('chapter'),
                'difficulty': data.get('difficulty'),
                'source_content': data.get('source_content')
            }
        )
        self.db.add(question)
        await self.db.commit()
        await self.db.refresh(question)
        return self._to_response(question)

    async def get_questions(
        self,
        skip: int = 0,
        limit: int = 20,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        question_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        chapter: Optional[str] = None,
        search: Optional[str] = None,
        page_from: Optional[int] = None,
        page_to: Optional[int] = None,
    ) -> QuestionListResponse:
        """獲取問題列表

        LEFT OUTER JOIN documents 取得來源文件的課本頁碼（source_page），
        並可用 page_from/page_to 依該頁碼區間篩選（語意與 documents 列表一致，
        見 app.core.page_range）；count 查詢套用相同的 join 與條件，確保分頁總數正確。
        """
        # 構建查詢條件
        conditions = []
        if subject:
            # 使用JSON操作符查詢科目
            conditions.append(_metadata_field('subject') == subject)
        if grade:
            # 使用JSON操作符查詢年級；'ALL' 為全年級通用教材，任何年級皆命中
            grade_col = _metadata_field('grade')
            conditions.append(or_(grade_col == grade, grade_col == 'ALL'))
        if question_type:
            conditions.append(Question.question_type == question_type)
        if difficulty:
            # 使用JSON操作符查詢難度
            conditions.append(_metadata_field('difficulty') == difficulty)
        if chapter:
            conditions.append(_metadata_field('chapter') == chapter)
        if search:
            conditions.append(Question.stem.ilike(f"%{search}%"))
        conditions.extend(page_range_conditions(Document.page_number, page_from, page_to))

        # 查詢總數（join documents，與資料查詢使用相同條件）
        count_stmt = select(func.count(Question.id)).outerjoin(
            Document, Question.document_id == Document.id
        )
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()

        # 查詢數據
        stmt = select(Question, Document.page_number).outerjoin(
            Document, Question.document_id == Document.id
        )
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.offset(skip).limit(limit).order_by(Question.created_at.desc())

        result = await self.db.execute(stmt)
        rows = result.all()

        pages = (total + limit - 1) // limit
        page = (skip // limit) + 1

        return QuestionListResponse(
            questions=[self._to_response(q, page_number) for q, page_number in rows],
            total=total,
            page=page,
            size=limit,
            pages=pages
        )

    async def get_question_by_id(self, question_id: int) -> Optional[QuestionResponse]:
        """根據ID獲取問題（含來源文件課本頁碼 source_page）"""
        stmt = (
            select(Question, Document.page_number)
            .outerjoin(Document, Question.document_id == Document.id)
            .where(Question.id == question_id)
        )
        result = await self.db.execute(stmt)
        row = result.first()
        if not row:
            return None
        question, page_number = row
        return self._to_response(question, page_number)

    async def get_facets(
        self,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        question_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        chapter: Optional[str] = None,
        page_from: Optional[int] = None,
        page_to: Optional[int] = None,
    ) -> Dict[str, Any]:
        """計算目前篩選條件下，subject/grade/question_type/chapter/difficulty 各自
        仍有資料的選項與筆數（faceted search），語意與 DocumentService.get_facets 一致：
        每個維度套用其他全部篩選條件但排除自己這個維度。
        page_from / page_to 與列表一樣依來源文件課本頁碼篩選（outer join documents）。
        """

        async def _facet(column, exclude: str, sort_key) -> list[Dict[str, Any]]:
            conditions = question_facet_conditions(
                exclude, subject, grade, question_type, difficulty, chapter, page_from, page_to
            )
            conditions.append(column.is_not(None))
            conditions.append(func.trim(column) != '')
            query = (
                select(column, func.count(Question.id))
                .select_from(Question)
                .outerjoin(Document, Question.document_id == Document.id)
                .where(and_(*conditions))
                .group_by(column)
            )
            result = await self.db.execute(query)
            items = [{'value': value, 'count': count} for value, count in result]
            items.sort(key=lambda item: sort_key(item['value']))
            return items

        subjects = await _facet(_metadata_field('subject'), 'subject', lambda v: v)
        grades = merge_all_grade_counts(await _facet(_metadata_field('grade'), 'grade', grade_sort_key))
        question_types = await _facet(Question.question_type, 'question_type', lambda v: v)
        chapters = await _facet(_metadata_field('chapter'), 'chapter', chapter_sort_key)
        difficulties = await _facet(_metadata_field('difficulty'), 'difficulty', lambda v: v)

        return {
            'subjects': subjects,
            'grades': grades,
            'question_types': question_types,
            'chapters': chapters,
            'difficulties': difficulties,
        }

    async def update_question(self, question_id: int, question_data: QuestionUpdate) -> Optional[QuestionResponse]:
        """更新問題"""
        stmt = select(Question).where(Question.id == question_id)
        result = await self.db.execute(stmt)
        question = result.scalar_one_or_none()
        
        if not question:
            return None

        # 映射欄位名稱以符合資料庫模型
        update_data = question_data.model_dump(exclude_unset=True)
        
        # 直接映射欄位
        if 'type' in update_data:
            question.question_type = update_data['type']
        if 'content' in update_data:
            question.stem = update_data['content']
        if 'options' in update_data:
            question.options = update_data['options']
        if 'correct_answer' in update_data:
            question.answer = update_data['correct_answer']
        if 'explanation' in update_data:
            question.explanation = update_data['explanation']

        # 改到題幹 / 選項 / 答案 / 題型時，用與生成相同的規則檢核並正規化；
        # 只改年級等 metadata 不檢核，避免舊資料無法更新。
        if any(k in update_data for k in ('type', 'content', 'options', 'correct_answer')):
            fields, problems = normalize_question_payload(
                question.question_type, question.stem, question.options,
                question.answer, question.question_data,
            )
            if problems:
                raise QuestionValidationError("題目格式不符，未更新：" + "；".join(problems))
            question.stem = fields["content"]
            question.answer = fields["answer"] if isinstance(fields["answer"], str) else json.dumps(fields["answer"], ensure_ascii=False)
            question.options = fields["options"]
            question.question_data = fields["question_data"]

        # 處理 source_metadata 中的欄位
        if 'subject' in update_data or 'grade' in update_data or 'chapter' in update_data or 'difficulty' in update_data:
            # 創建新的字典副本以確保 SQLAlchemy 偵測到變更
            metadata = dict(question.source_metadata) if question.source_metadata else {}

            if 'subject' in update_data:
                metadata['subject'] = update_data['subject']
            if 'grade' in update_data:
                metadata['grade'] = update_data['grade']
            if 'chapter' in update_data:
                metadata['chapter'] = update_data['chapter']
            if 'difficulty' in update_data:
                metadata['difficulty'] = update_data['difficulty']

            # 重新指派整個字典以觸發 SQLAlchemy 的變更偵測
            question.source_metadata = metadata

        await self.db.commit()
        await self.db.refresh(question)
        return self._to_response(question)

    async def delete_question(self, question_id: int) -> bool:
        """刪除問題"""
        stmt = select(Question).where(Question.id == question_id)
        result = await self.db.execute(stmt)
        question = result.scalar_one_or_none()

        if not question:
            return False

        await self.db.delete(question)
        await self.db.commit()
        return True

    async def batch_delete_questions(self, ids: list[int]) -> dict:
        """批量刪除問題"""
        success_count = 0
        failed_ids = []

        for question_id in ids:
            try:
                stmt = select(Question).where(Question.id == question_id)
                result = await self.db.execute(stmt)
                question = result.scalar_one_or_none()

                if question:
                    await self.db.delete(question)
                    success_count += 1
                else:
                    failed_ids.append(question_id)
            except Exception:
                failed_ids.append(question_id)

        await self.db.commit()

        return {
            "success_count": success_count,
            "failed_count": len(failed_ids),
            "failed_ids": failed_ids
        }

    async def get_question_stats(self) -> QuestionStatsResponse:
        """獲取問題統計"""
        # 總問題數
        total_stmt = select(func.count(Question.id))
        total_result = await self.db.execute(total_stmt)
        total_questions = total_result.scalar()

        # 按類型統計
        type_stmt = select(Question.question_type, func.count(Question.id)).group_by(Question.question_type)
        type_result = await self.db.execute(type_stmt)
        by_type = {row[0]: row[1] for row in type_result.fetchall()}

        # 按科目統計 (從 source_metadata 中提取)
        # 由於科目存儲在 JSON 中，我們需要使用 PostgreSQL 的 JSON 操作符
        from sqlalchemy import text
        subject_stmt = text("""
            SELECT source_metadata->>'subject' as subject, COUNT(id)
            FROM questions 
            WHERE source_metadata->>'subject' IS NOT NULL
            GROUP BY source_metadata->>'subject'
        """)
        subject_result = await self.db.execute(subject_stmt)
        by_subject = {row[0] or "未分類": row[1] for row in subject_result.fetchall()}

        # 按難度統計
        difficulty_stmt = text("""
            SELECT COALESCE(source_metadata->>'difficulty', 'medium') as difficulty, COUNT(id)
            FROM questions
            GROUP BY COALESCE(source_metadata->>'difficulty', 'medium')
        """)
        difficulty_result = await self.db.execute(difficulty_stmt)
        by_difficulty = {row[0]: row[1] for row in difficulty_result.fetchall()}

        # 按年級統計 (從 source_metadata 中提取)
        grade_stmt = text("""
            SELECT source_metadata->>'grade' as grade, COUNT(id)
            FROM questions
            WHERE source_metadata->>'grade' IS NOT NULL
            GROUP BY source_metadata->>'grade'
        """)
        grade_result = await self.db.execute(grade_stmt)
        by_grade = {str(row[0]): int(row[1]) for row in grade_result.fetchall() if row[0]}

        return QuestionStatsResponse(
            total_questions=total_questions,
            by_type=by_type,
            by_subject=by_subject,
            by_difficulty=by_difficulty,
            by_grade=by_grade
        )

    async def export_questions(
        self,
        format: str,
        subject: Optional[str] = None,
        question_type: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """導出問題"""
        # 構建查詢條件
        conditions = []
        if subject:
            conditions.append(Question.source_metadata.op('->>')(literal_column("'subject'")) == subject)
        if question_type:
            conditions.append(Question.question_type == question_type)
        if difficulty:
            conditions.append(Question.source_metadata.op('->>')(literal_column("'difficulty'")) == difficulty)

        # 查詢數據
        stmt = select(Question)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(Question.created_at.desc())
        
        result = await self.db.execute(stmt)
        questions = result.scalars().all()

        # 轉換為字典格式
        questions_data = []
        for q in questions:
            questions_data.append({
                "id": q.id,
                "type": q.type,
                "content": q.content,
                "options": q.options,
                "correct_answer": q.correct_answer,
                "explanation": q.explanation,
                "source_document_id": q.source_document_id,
                "source_content": q.source_content,
                "subject": q.subject,
                "chapter": q.chapter,
                "difficulty": q.difficulty,
                "created_at": q.created_at.isoformat() if q.created_at else None,
                "updated_at": q.updated_at.isoformat() if q.updated_at else None
            })

        if format.lower() == "json":
            return {
                "filename": f"questions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "content": json.dumps(questions_data, ensure_ascii=False, indent=2),
                "content_type": "application/json"
            }
        
        elif format.lower() == "csv":
            output = StringIO()
            if questions_data:
                fieldnames = questions_data[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(questions_data)
            
            return {
                "filename": f"questions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "content": output.getvalue(),
                "content_type": "text/csv"
            }
        
        elif format.lower() == "xlsx":
            df = pd.DataFrame(questions_data)
            output = StringIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Questions', index=False)
            
            return {
                "filename": f"questions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "content": output.getvalue(),
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
        
        else:
            raise ValueError(f"Unsupported format: {format}")


class MockQuestionService:
    """Mock 問題管理服務"""
    
    def __init__(self):
        self.mock_questions = [
            {
                "id": 1,
                "type": "single_choice",
                "content": "哪個器官負責將血液循環到全身？",
                "options": ["心臟", "肺部", "肝臟", "腎臟"],
                "correct_answer": "心臟",
                "explanation": "心臟是循環系統的中心器官，負責泵送血液到全身各個部位。",
                "subject": "Health",
                "chapter": "Chapter 7 Your Transportation System", 
                "difficulty": "easy",
                "created_at": "2025-08-27T10:00:00Z",
                "updated_at": "2025-08-27T10:00:00Z"
            },
            {
                "id": 2,
                "type": "cloze",
                "content": "血液中的______攜帶氧氣到身體各部位。",
                "correct_answer": "紅血球",
                "explanation": "紅血球含有血紅蛋白，能夠結合氧氣並運輸到身體各個組織。",
                "subject": "Health",
                "chapter": "Chapter 6 Your Transportation System",
                "difficulty": "medium",
                "created_at": "2025-08-27T11:00:00Z", 
                "updated_at": "2025-08-27T11:00:00Z"
            }
        ]

    async def get_questions(self, skip: int = 0, limit: int = 20, **filters) -> QuestionListResponse:
        questions = self.mock_questions[skip:skip+limit]
        return QuestionListResponse(
            questions=questions,
            total=len(self.mock_questions),
            page=(skip // limit) + 1,
            size=limit,
            pages=(len(self.mock_questions) + limit - 1) // limit
        )

    async def get_question_stats(self) -> QuestionStatsResponse:
        return QuestionStatsResponse(
            total_questions=len(self.mock_questions),
            by_type={"single_choice": 1, "cloze": 1},
            by_subject={"Health": 2},
            by_difficulty={"easy": 1, "medium": 1},
            by_grade={"G1": 1, "G2": 1}
        )

    async def get_facets(
        self,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        question_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        chapter: Optional[str] = None,
        page_from: Optional[int] = None,
        page_to: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Mock 版 facets：記憶體樣本資料套用與真實模式相同的「排除自身維度」邏輯。

        樣本資料用 'type' 存題型（對應真實模式的 question_type 欄位）且沒有 'grade' 鍵，
        以 .get() 容錯；頁碼依 'source_page'（沒有就視為解析不出來，給了範圍就排除）。
        """

        def _matches(row: Dict[str, Any], exclude: str) -> bool:
            if page_from is not None or page_to is not None:
                parsed = parse_page_range(row.get('source_page'))
                if parsed is None:
                    return False
                start, end = parsed
                if page_from is not None and end < page_from:
                    return False
                if page_to is not None and start > page_to:
                    return False
            if exclude != 'subject' and subject and row.get('subject') != subject:
                return False
            if exclude != 'grade' and grade:
                row_grade = row.get('grade')
                if row_grade != grade and row_grade != 'ALL':
                    return False
            if exclude != 'question_type' and question_type and row.get('type') != question_type:
                return False
            if exclude != 'difficulty' and difficulty and row.get('difficulty') != difficulty:
                return False
            if exclude != 'chapter' and chapter and row.get('chapter') != chapter:
                return False
            return True

        def _facet(field: str, exclude: str, sort_key) -> list[Dict[str, Any]]:
            counts: Dict[str, int] = {}
            for row in self.mock_questions:
                if not _matches(row, exclude):
                    continue
                value = row.get(field)
                if not value or not str(value).strip():
                    continue
                counts[value] = counts.get(value, 0) + 1
            items = [{'value': value, 'count': count} for value, count in counts.items()]
            items.sort(key=lambda item: sort_key(item['value']))
            return items

        return {
            'subjects': _facet('subject', 'subject', lambda v: v),
            'grades': merge_all_grade_counts(_facet('grade', 'grade', grade_sort_key)),
            'question_types': _facet('type', 'question_type', lambda v: v),
            'chapters': _facet('chapter', 'chapter', chapter_sort_key),
            'difficulties': _facet('difficulty', 'difficulty', lambda v: v),
        }