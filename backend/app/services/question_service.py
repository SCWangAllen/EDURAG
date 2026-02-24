from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, literal_column
from app.db.models import Question
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse, QuestionListResponse, QuestionStatsResponse
import json
import csv
from io import StringIO
import pandas as pd
from datetime import datetime


class QuestionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_response(self, question: Question) -> QuestionResponse:
        """將資料庫 Question 模型轉換為 QuestionResponse schema"""
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
        search: Optional[str] = None
    ) -> QuestionListResponse:
        """獲取問題列表"""
        # 構建查詢條件
        conditions = []
        if subject:
            # 使用JSON操作符查詢科目
            conditions.append(Question.source_metadata.op('->>')(literal_column("'subject'")) == subject)
        if grade:
            # 使用JSON操作符查詢年級
            conditions.append(Question.source_metadata.op('->>')(literal_column("'grade'")) == grade)
        if question_type:
            conditions.append(Question.question_type == question_type)
        if difficulty:
            # 使用JSON操作符查詢難度
            conditions.append(Question.source_metadata.op('->>')(literal_column("'difficulty'")) == difficulty)
        if search:
            conditions.append(Question.stem.ilike(f"%{search}%"))

        # 查詢總數
        count_stmt = select(func.count(Question.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()

        # 查詢數據
        stmt = select(Question)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.offset(skip).limit(limit).order_by(Question.created_at.desc())
        
        result = await self.db.execute(stmt)
        questions = result.scalars().all()

        pages = (total + limit - 1) // limit
        page = (skip // limit) + 1

        return QuestionListResponse(
            questions=[self._to_response(q) for q in questions],
            total=total,
            page=page,
            size=limit,
            pages=pages
        )

    async def get_question_by_id(self, question_id: int) -> Optional[QuestionResponse]:
        """根據ID獲取問題"""
        stmt = select(Question).where(Question.id == question_id)
        result = await self.db.execute(stmt)
        question = result.scalar_one_or_none()
        return self._to_response(question) if question else None

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