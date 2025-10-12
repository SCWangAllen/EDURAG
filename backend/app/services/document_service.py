from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from app.db.models import Document, Embedding, Question
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_documents(
        self,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        chapter: Optional[str] = None,
        search_query: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """取得文件清單"""

        # 建立基本查詢
        query = select(Document)
        count_query = select(func.count(Document.id))

        # 添加篩選條件
        conditions = []

        if subject:
            conditions.append(Document.subject == subject)

        if grade:
            conditions.append(Document.grade == grade)

        if chapter:
            conditions.append(Document.chapter.ilike(f'%{chapter}%'))

        if search_query:
            conditions.append(
                or_(
                    Document.title.ilike(f'%{search_query}%'),
                    Document.content.ilike(f'%{search_query}%'),
                    Document.chapter.ilike(f'%{search_query}%')
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # 添加排序和分頁
        query = query.order_by(Document.created_at.desc()).offset(skip).limit(limit)
        
        # 執行查詢
        result = await self.db.execute(query)
        documents = result.scalars().all()
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # 轉換為字典格式
        documents_data = []
        for doc in documents:
            doc_data = {
                'id': doc.id,
                'title': doc.title,
                'content': doc.content,  # 返回完整內容，不截斷
                'subject': doc.subject,
                'grade': doc.grade,
                'chapter': doc.chapter,
                'page_number': doc.page_number,
                'image_filename': doc.image_filename,
                'created_at': doc.created_at.isoformat() if doc.created_at else None,
                'updated_at': doc.updated_at.isoformat() if doc.updated_at else None
            }
            documents_data.append(doc_data)
        
        return {
            'documents': documents_data,
            'total': total,
            'page': (skip // limit) + 1,
            'size': limit,
            'pages': (total + limit - 1) // limit
        }

    async def get_document_by_id(self, document_id: int) -> Optional[Dict[str, Any]]:
        """依 ID 取得文件詳情"""
        query = select(Document).where(Document.id == document_id)
        result = await self.db.execute(query)
        document = result.scalar_one_or_none()
        
        if not document:
            return None
            
        return {
            'id': document.id,
            'title': document.title,
            'content': document.content,
            'subject': document.subject,
            'grade': document.grade,
            'chapter': document.chapter,
            'image_filename': document.image_filename,
            'image_data': document.image_data,
            'page_number': document.page_number,
            'import_source': document.import_source,
            'created_at': document.created_at.isoformat() if document.created_at else None,
            'updated_at': document.updated_at.isoformat() if document.updated_at else None
        }

    async def search_documents(
        self,
        query_text: str,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """搜尋文件"""

        # 基本文字搜尋
        search_conditions = [
            or_(
                Document.title.ilike(f'%{query_text}%'),
                Document.content.ilike(f'%{query_text}%'),
                Document.chapter.ilike(f'%{query_text}%')
            )
        ]

        if subject:
            search_conditions.append(Document.subject == subject)

        if grade:
            search_conditions.append(Document.grade == grade)
        
        query = select(Document).where(and_(*search_conditions)).limit(limit)
        result = await self.db.execute(query)
        documents = result.scalars().all()
        
        search_results = []
        for doc in documents:
            # 計算相關性分數（簡單實現）
            relevance_score = 0
            query_lower = query_text.lower()
            
            if query_lower in doc.title.lower():
                relevance_score += 0.3
            if query_lower in doc.content.lower():
                relevance_score += 0.2
            if query_lower in (doc.chapter or '').lower():
                relevance_score += 0.1
                
            search_results.append({
                'id': doc.id,
                'title': doc.title,
                'content': doc.content,  # 返回完整內容，不截斷
                'subject': doc.subject,
                'grade': doc.grade,
                'chapter': doc.chapter,
                'relevance_score': relevance_score,
                'created_at': doc.created_at.isoformat() if doc.created_at else None
            })
        
        # 依相關性排序
        search_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return search_results

    async def get_document_stats(self) -> Dict[str, Any]:
        """取得文件統計"""
        
        # 總文件數
        total_count = await self.db.scalar(select(func.count(Document.id)))
        
        # 依科目統計
        subject_stats = await self.db.execute(
            select(Document.subject, func.count(Document.id))
            .group_by(Document.subject)
            .order_by(func.count(Document.id).desc())
        )
        
        subjects = {}
        for subject, count in subject_stats:
            subjects[subject or 'Unknown'] = count
            
        # 依章節統計
        chapter_stats = await self.db.execute(
            select(Document.chapter, func.count(Document.id))
            .where(Document.chapter.is_not(None))
            .group_by(Document.chapter)
            .order_by(func.count(Document.id).desc())
            .limit(10)
        )
        
        chapters = {}
        for chapter, count in chapter_stats:
            chapters[chapter] = count
        
        return {
            'total_documents': total_count,
            'subjects': subjects,
            'top_chapters': chapters,
            'has_images': await self.db.scalar(
                select(func.count(Document.id))
                .where(Document.image_filename.is_not(None))
            )
        }

    async def get_subjects(self) -> List[str]:
        """取得所有科目清單"""
        query = (
            select(Document.subject)
            .where(Document.subject.is_not(None))
            .distinct()
            .order_by(Document.subject)
        )
        result = await self.db.execute(query)
        return [subject for (subject,) in result]

    async def get_chapters_by_subject(self, subject: str) -> List[str]:
        """取得特定科目的章節清單"""
        query = (
            select(Document.chapter)
            .where(
                and_(
                    Document.subject == subject,
                    Document.chapter.is_not(None)
                )
            )
            .distinct()
            .order_by(Document.chapter)
        )
        result = await self.db.execute(query)
        return [chapter for (chapter,) in result]

    async def create_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """創建新文件"""
        document = Document(
            title=document_data['title'],
            content=document_data['content'],
            subject=document_data['subject'],
            grade=document_data.get('grade'),
            chapter=document_data.get('chapter'),
            page_number=document_data.get('page_number'),
            image_filename=document_data.get('image_filename'),
            import_source=document_data.get('import_source', 'manual')
        )

        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)

        return {
            'id': document.id,
            'title': document.title,
            'content': document.content,
            'subject': document.subject,
            'grade': document.grade,
            'chapter': document.chapter,
            'page_number': document.page_number,
            'image_filename': document.image_filename,
            'import_source': document.import_source,
            'created_at': document.created_at.isoformat() if document.created_at else None,
            'updated_at': document.updated_at.isoformat() if document.updated_at else None
        }

    async def update_document(self, document_id: int, document_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新文件"""
        document = await self.get_document_by_id(document_id)
        if not document:
            return None
        
        # 更新文件記錄
        from sqlalchemy import update
        
        update_data = {}
        for key in ['title', 'content', 'subject', 'grade', 'chapter', 'page_number', 'image_filename']:
            if key in document_data:
                update_data[key] = document_data[key]
        
        if update_data:
            query = (
                update(Document)
                .where(Document.id == document_id)
                .values(**update_data)
            )
            await self.db.execute(query)
            await self.db.commit()
        
        return await self.get_document_by_id(document_id)

    async def check_document_references(self, document_id: int) -> Dict[str, Any]:
        """檢查文件是否被其他資料引用"""
        # 檢查相關問題數量
        question_count = await self.db.scalar(
            select(func.count(Question.id)).where(Question.document_id == document_id)
        )
        
        # 檢查相關嵌入向量數量
        embedding_count = await self.db.scalar(
            select(func.count(Embedding.id)).where(Embedding.document_id == document_id)
        )
        
        return {
            'questions': question_count or 0,
            'embeddings': embedding_count or 0,
            'has_references': (question_count or 0) > 0 or (embedding_count or 0) > 0
        }

    async def delete_document(self, document_id: int, force: bool = False) -> Dict[str, Any]:
        """刪除文件
        
        Args:
            document_id: 文件 ID
            force: 是否強制刪除（同時刪除相關問題和嵌入向量）
            
        Returns:
            Dict 包含刪除結果和相關資訊
        """
        document = await self.get_document_by_id(document_id)
        if not document:
            return {
                'success': False,
                'error': 'Document not found',
                'error_type': 'not_found'
            }
        
        # 檢查引用
        references = await self.check_document_references(document_id)
        
        if references['has_references'] and not force:
            return {
                'success': False,
                'error': 'Document has references',
                'error_type': 'has_references',
                'references': references
            }
        
        from sqlalchemy import delete
        
        try:
            # 如果強制刪除，先刪除相關資料
            if force:
                # 刪除相關問題
                if references['questions'] > 0:
                    await self.db.execute(
                        delete(Question).where(Question.document_id == document_id)
                    )
                
                # 刪除相關嵌入向量
                if references['embeddings'] > 0:
                    await self.db.execute(
                        delete(Embedding).where(Embedding.document_id == document_id)
                    )
            
            # 刪除文件
            await self.db.execute(
                delete(Document).where(Document.id == document_id)
            )
            await self.db.commit()
            
            return {
                'success': True,
                'deleted_references': references if force else {'questions': 0, 'embeddings': 0}
            }
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete document {document_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'database_error'
            }


# Mock 版本（用於測試模式）
class MockDocumentService:
    """Mock 文件服務"""
    
    def __init__(self):
        # 使用實際匯入的資料作為 Mock 資料結構
        self.documents = [
            {
                'id': i + 1,
                'title': f'Health Education Chapter {i + 1}',
                'content': f'This is sample health education content for chapter {i + 1}...',
                'subject': 'Health',
                'grade': f'G{(i % 6) + 1}',  # 均勻分配 G1-G6
                'chapter': f'Chapter {i + 1}',
                'image_filename': f'health_image_{i + 1}.jpg' if i % 3 == 0 else None,
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z'
            }
            for i in range(13)
        ]

    async def get_documents(
        self,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        chapter: Optional[str] = None,
        search_query: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """取得文件清單"""
        filtered_docs = self.documents.copy()

        if subject:
            filtered_docs = [d for d in filtered_docs if d['subject'] == subject]

        if grade:
            filtered_docs = [d for d in filtered_docs if d.get('grade') == grade]

        if chapter:
            filtered_docs = [d for d in filtered_docs if chapter.lower() in d['chapter'].lower()]

        if search_query:
            filtered_docs = [
                d for d in filtered_docs
                if search_query.lower() in d['title'].lower()
                or search_query.lower() in d['content'].lower()
            ]
        
        total = len(filtered_docs)
        paginated_docs = filtered_docs[skip:skip + limit]
        
        return {
            'documents': paginated_docs,
            'total': total,
            'page': (skip // limit) + 1,
            'size': limit,
            'pages': (total + limit - 1) // limit
        }

    async def get_document_stats(self) -> Dict[str, Any]:
        return {
            'total_documents': len(self.documents),
            'subjects': {'Health': len(self.documents)},
            'top_chapters': {f'Chapter {i}': 1 for i in range(1, 6)},
            'has_images': len([d for d in self.documents if d['image_filename']])
        }