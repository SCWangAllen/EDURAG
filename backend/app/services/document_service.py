from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, cast, case, delete, Integer, Text
from app.db.models import Document, Embedding, Question
from app.core.subject_norm import GRADE_SORT_INDEX, VALID_GRADES, grade_sort_key, normalize_subject
from app.core.page_range import page_range_conditions, parse_page_range
from typing import List, Optional, Dict, Any
import logging
import math
import re

logger = logging.getLogger(__name__)

# 章節數字上限抓 9 位數（cast 成 Integer 前先夾住位數，避免超長數字 overflow 32-bit int 觸發 500）
_CHAPTER_DIGITS = r'\d{1,9}'
_CHAPTER_NUM_RE = re.compile(_CHAPTER_DIGITS)


def chapter_sort_key(chapter: Optional[str]) -> tuple:
    """章節自然排序 key，語意對齊真實 DB 的
    `substring(chapter from '\\d{1,9}')::int NULLS LAST, chapter ASC`。

    純函式，供 MockDocumentService 與測試共用，確保 mock/real 排序結果一致。
    回傳 (數字或 +inf, 是否為 None, 文字)：數字小的在前；無數字或 None 視為 +inf 排最後；
    None 再用是否為 None 的旗標排在「有文字但無數字」的項目之後（對齊 SQL NULLS LAST）。
    """
    if chapter is None:
        return (math.inf, True, "")
    match = _CHAPTER_NUM_RE.search(chapter)
    num = int(match.group()) if match else math.inf
    return (num, False, chapter)


def _match_key(
    subject: Optional[str],
    grade: Optional[str],
    chapter: Optional[str],
    title: Optional[str],
    page_number: Optional[str],
) -> tuple[str, str, str, str, str]:
    """正規化後的比對鍵：科目正規化、年級大寫、章節/標題/頁碼 trim 後小寫。

    頁碼是同一章節下區分不同列的關鍵（title 由 chapter 首行推導，同章節多列
    通常會是同一個 title），純函式，供重新上傳比對重用。
    """
    return (
        normalize_subject(subject).lower() if subject else "",
        (grade or "").strip().upper(),
        (chapter or "").strip().lower(),
        (title or "").strip().lower(),
        (page_number or "").strip().lower(),
    )


def find_replacement_targets(
    existing_rows: list[dict[str, Any]],
    new_docs: list[dict[str, Any]],
) -> tuple[dict[Any, int], set[Any]]:
    """比對「重新上傳」是否該取代既有文件而非新增一筆。

    純函式，不觸 DB。existing_rows 需含 id/subject/grade/chapter/title/page_number；
    new_docs 需含 index（回傳字典的 key）與同樣五個欄位。
    正規化科目 + 年級（大小寫不敏感）+ trim 後小寫的章節/標題/頁碼完全相同視為同一份文件。

    當 key 在既有資料或本次上傳中不唯一時視為「模糊」——不猜測，一律當新增，
    並把該 new_doc 的 index 放進回傳的 ambiguous set，由呼叫端加上警示。
    每個既有 id 最多被消耗一次（防呆；正常情況下 key 唯一即已保證這點）。

    回傳 (mapping, ambiguous_indices)：
      mapping = {new_doc["index"]: existing_document_id}，只含明確命中的項目。
      ambiguous_indices = 因 key 模糊而被跳過取代的 new_doc index 集合。
    """
    existing_ids_by_key: dict[tuple, list[int]] = {}
    for row in existing_rows:
        key = _match_key(
            row.get("subject"), row.get("grade"), row.get("chapter"),
            row.get("title"), row.get("page_number"),
        )
        existing_id = row.get("id")
        if existing_id is None:
            continue
        existing_ids_by_key.setdefault(key, []).append(existing_id)

    new_doc_keys: dict[Any, tuple] = {}
    new_key_counts: dict[tuple, int] = {}
    for doc in new_docs:
        key = _match_key(
            doc.get("subject"), doc.get("grade"), doc.get("chapter"),
            doc.get("title"), doc.get("page_number"),
        )
        new_doc_keys[doc["index"]] = key
        new_key_counts[key] = new_key_counts.get(key, 0) + 1

    mapping: dict[Any, int] = {}
    ambiguous: set[Any] = set()
    used_existing_ids: set[int] = set()

    for doc in new_docs:
        index = doc["index"]
        key = new_doc_keys[index]
        ids = existing_ids_by_key.get(key)
        if not ids:
            continue  # 沒有命中既有資料，當新增即可

        if len(ids) > 1 or new_key_counts[key] > 1:
            # 既有資料或本次上傳有多筆共用同一個 key，無法確定該取代哪一筆
            ambiguous.add(index)
            continue

        existing_id = ids[0]
        if existing_id in used_existing_ids:
            ambiguous.add(index)
            continue

        mapping[index] = existing_id
        used_existing_ids.add(existing_id)

    return mapping, ambiguous


def plan_document_copies(
    existing_rows: list[dict[str, Any]],
    docs: list[dict[str, Any]],
    target_grades: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """規劃「複製文件到其他年級」該建立哪些新文件、略過哪些 (文件, 目標年級) 組合。

    純函式，不觸 DB，供 DocumentService.copy_documents_to_grades 與測試共用。
    existing_rows 為既有文件的比對用最小欄位（id/subject/grade/chapter/title/page_number，
    通常已限縮為「來源文件所屬科目 × 目標年級」的候選集合，避免整表掃描）；
    docs 為要複製的來源文件（需含 id/subject/grade/chapter/title/page_number）；
    target_grades 為已正規化（見 subject_norm.normalize_grade）的目標年級代碼清單。

    每個 (doc, grade) 組合依序判斷：
      - grade 與來源文件自身年級相同（正規化後大小寫不敏感比對）→ 略過（"same grade"）
      - 命中既有文件（正規化科目 + 年級 + 章節 + 標題 + 頁碼皆相同，沿用 _match_key）
        → 略過（"exists"）
      - 否則排入 to_create

    同一批次內若有多個來源文件複製到同一目標年級後會產生相同 key，只有第一個會被
    排入 to_create、其餘視為 "exists" 略過，避免同一請求內重複建立完全相同的文件。

    回傳 (to_create, skipped_items)：
      to_create = [{"source": doc, "grade": grade}, ...]
      skipped_items = [{"document_id": doc["id"], "grade": grade, "reason": reason}, ...]
    """
    existing_keys: set[tuple] = set()
    for row in existing_rows:
        existing_keys.add(_match_key(
            row.get("subject"), row.get("grade"), row.get("chapter"),
            row.get("title"), row.get("page_number"),
        ))

    to_create: list[dict[str, Any]] = []
    skipped_items: list[dict[str, Any]] = []

    for doc in docs:
        doc_grade_norm = (doc.get("grade") or "").strip().upper()
        for grade in target_grades:
            if grade == doc_grade_norm:
                skipped_items.append({
                    "document_id": doc["id"], "grade": grade, "reason": "same grade",
                })
                continue

            key = _match_key(
                doc.get("subject"), grade, doc.get("chapter"),
                doc.get("title"), doc.get("page_number"),
            )
            if key in existing_keys:
                skipped_items.append({
                    "document_id": doc["id"], "grade": grade, "reason": "exists",
                })
                continue

            to_create.append({"source": doc, "grade": grade})
            existing_keys.add(key)  # 避免同一批次內對同一目標 key 重複建立

    return to_create, skipped_items


def source_scope_conditions(
    source_filename: Optional[str] = None,
    subject: Optional[str] = None,
    grade: Optional[str] = None,
) -> list:
    """「上傳檔案」相關查詢共用的篩選條件（純函數，可直接編譯 SQL 做測試）。

    - source_filename 給了就限定該來源檔名；None 時只排除沒有檔名的舊資料
    - subject / grade 與文件列表的篩選一致：帶了就只算 / 只刪該科目、該年級
    """
    conditions = [
        Document.source_filename == source_filename
        if source_filename is not None
        else Document.source_filename.is_not(None)
    ]
    if subject:
        conditions.append(Document.subject == subject)
    if grade:
        conditions.append(Document.grade == grade)
    return conditions


def sources_query(subject: Optional[str] = None, grade: Optional[str] = None):
    """上傳來源檔名清單的查詢（distinct 檔名、文件數、最新上傳時間，新到舊）。"""
    return (
        select(
            Document.source_filename,
            func.count(Document.id),
            func.max(Document.created_at),
        )
        .where(and_(*source_scope_conditions(None, subject, grade)))
        .group_by(Document.source_filename)
        .order_by(func.max(Document.created_at).desc())
    )


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _apply_sort(self, query, sort: str):
        """sort="newest" 依建立時間新到舊；預設 "chapter" 依科目→年級→章節自然數字→章節文字→標題→id 排序。"""
        if sort == "newest":
            return query.order_by(Document.created_at.desc())

        # 章節自然排序：從章節文字取出第一個數字（最多 9 位，避免超長數字 cast 成 Integer 時 overflow）；
        # 無數字排最後；最後補 id 排序，讓完全同 key（含重複資料）時分頁結果穩定
        chapter_num = cast(func.substring(cast(Document.chapter, Text), _CHAPTER_DIGITS), Integer)
        # 年級依 band 唯一權威順序排序（ESL → 年級班 → 國中班 → ALL 最後），而非依字母排序
        # （字母排序會讓 'JR4' 排在 'G4' 前面、'ALL' 排在最前面，不符合實際 band 順序）。
        grade_order = case(GRADE_SORT_INDEX, value=Document.grade, else_=len(VALID_GRADES))
        return query.order_by(
            Document.subject.asc(),
            grade_order.asc(),
            chapter_num.asc().nulls_last(),
            Document.chapter.asc(),
            Document.title.asc(),
            Document.id.asc(),
        )

    async def get_documents(
        self,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        chapter: Optional[str] = None,
        search_query: Optional[str] = None,
        source_file: Optional[str] = None,
        sort: str = "chapter",
        skip: int = 0,
        limit: Optional[int] = None,
        page_from: Optional[int] = None,
        page_to: Optional[int] = None,
    ) -> Dict[str, Any]:
        """取得文件清單（limit 為 None 時回傳全部）

        page_from / page_to：依 page_number（自由格式文字，見 app.core.page_range）
        解析出的頁碼區間篩選，讓教師能用「頁 115-171」描述考試範圍。
        """

        # 建立基本查詢
        query = select(Document)
        count_query = select(func.count(Document.id))

        # 添加篩選條件
        conditions = []

        if subject:
            conditions.append(Document.subject == subject)

        if grade:
            # 'ALL' 為全年級通用教材，任何年級篩選皆命中
            conditions.append(or_(Document.grade == grade, Document.grade == 'ALL'))

        if chapter:
            conditions.append(Document.chapter.ilike(f'%{chapter}%'))

        if source_file:
            conditions.append(Document.source_filename == source_file)

        conditions.extend(page_range_conditions(Document.page_number, page_from, page_to))

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
        query = self._apply_sort(query, sort).offset(skip).limit(limit)

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
                'source_filename': doc.source_filename,
                'created_at': doc.created_at.isoformat() if doc.created_at else None,
                'updated_at': doc.updated_at.isoformat() if doc.updated_at else None
            }
            documents_data.append(doc_data)

        return {
            'documents': documents_data,
            'total': total,
            'page': (skip // limit) + 1 if limit else 1,
            'size': limit if limit else total,
            'pages': (total + limit - 1) // limit if limit else 1
        }

    async def get_sources(
        self, subject: Optional[str] = None, grade: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """取得所有上傳來源檔名清單（distinct 檔名、文件數、最新上傳時間），依最新時間新到舊。

        subject / grade 可選，帶入時僅統計符合該科目/年級篩選條件的文件，
        供「上傳檔案」下拉選單依目前的科目/年級篩選動態列出符合條件的來源檔名。
        """
        result = await self.db.execute(sources_query(subject, grade))
        return [
            {
                'source_filename': source_filename,
                'count': count,
                'latest': latest.isoformat() if latest else None,
            }
            for source_filename, count, latest in result
        ]

    async def delete_documents_by_source(
        self,
        source_filename: str,
        force: bool = False,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
    ) -> Dict[str, Any]:
        """刪除某個上傳來源檔名底下的全部文件（可再以 subject / grade 限縮，與列表篩選一致）。

        與 batch_delete_documents 的差異:
        - 引用檢查一次查完(group by document_id),不逐筆 N+1;一批 400 筆只需 4 個查詢。
        - 只有「被題目引用」才算阻擋;embeddings 隨文件一起刪(DB 亦有 ON DELETE CASCADE),
          否則每份已向量化的文件都會被判定有引用,非 force 永遠刪不掉。

        Args:
            source_filename: 上傳來源檔名（Document.source_filename）
            force: 強制刪除時連同引用的題目一併刪除
            subject / grade: 限定科目 / 年級(None 表示不限)

        Returns:
            success_count / failed_count / failed([{id, reason}]) / total / source_filename
        """
        conditions = source_scope_conditions(source_filename, subject, grade)
        rows = await self.db.execute(select(Document.id).where(and_(*conditions)))
        document_ids = [row[0] for row in rows]

        def _result(success: int, failed: List[Dict[str, Any]]) -> Dict[str, Any]:
            return {
                'success_count': success,
                'failed_count': len(failed),
                'failed': failed,
                'total': len(document_ids),
                'source_filename': source_filename,
            }

        if not document_ids:
            return _result(0, [])

        ref_rows = await self.db.execute(
            select(Question.document_id, func.count(Question.id))
            .where(Question.document_id.in_(document_ids))
            .group_by(Question.document_id)
        )
        referenced = {doc_id: count for doc_id, count in ref_rows}

        if force:
            deletable = document_ids
            failed: List[Dict[str, Any]] = []
        else:
            deletable = [doc_id for doc_id in document_ids if doc_id not in referenced]
            failed = [
                {'id': doc_id, 'reason': f"被 {referenced[doc_id]} 題引用"}
                for doc_id in document_ids
                if doc_id in referenced
            ]

        if deletable:
            if force and referenced:
                await self.db.execute(
                    delete(Question).where(Question.document_id.in_(list(referenced)))
                )
            await self.db.execute(
                delete(Embedding).where(Embedding.document_id.in_(deletable))
            )
            await self.db.execute(delete(Document).where(Document.id.in_(deletable)))
            await self.db.commit()

        logger.info(
            f"delete_documents_by_source('{source_filename}', force={force}, "
            f"subject={subject}, grade={grade}): {len(deletable)} deleted, {len(failed)} kept"
        )
        return _result(len(deletable), failed)
    async def get_documents_for_matching(
        self, subject_grade_pairs: Optional[list[tuple[Optional[str], Optional[str]]]] = None
    ) -> list[dict[str, Any]]:
        """取得比對用最小欄位（id/subject/grade/chapter/title/page_number），供重新上傳判斷是否取代既有文件。

        subject_grade_pairs 限縮查詢範圍到本次上傳實際出現的 (subject, grade) 組合，
        避免每次上傳都整表掃描；傳 None 或空清單時回傳空清單（呼叫端沒有可比對的資料）。
        """
        if not subject_grade_pairs:
            return []

        conditions = []
        for subject, grade in set(subject_grade_pairs):
            subject_cond = Document.subject == subject
            grade_cond = Document.grade.is_(None) if grade is None else Document.grade == grade
            conditions.append(and_(subject_cond, grade_cond))

        query = select(
            Document.id, Document.subject, Document.grade, Document.chapter,
            Document.title, Document.page_number,
        ).where(or_(*conditions))
        result = await self.db.execute(query)
        return [
            {
                'id': r.id, 'subject': r.subject, 'grade': r.grade, 'chapter': r.chapter,
                'title': r.title, 'page_number': r.page_number,
            }
            for r in result
        ]

    async def replace_document(self, document_id: int, document_data: dict[str, Any]) -> bool:
        """以新內容整批取代既有文件（同一列 UPDATE）。

        注意：刻意不刪除/重建 embeddings。目前 Excel 上傳流程（save_documents）本身
        不會為新建文件產生 embedding（embedding 只透過獨立的 /api/ingest 端點產生，
        其分塊+向量化邏輯與該端點的 request/response 緊密耦合，抽成可重用函式屬於
        較大範圍的重構，不在本次修正範圍）。若貿然在這裡清掉舊 embeddings，等於讓
        曾經 ingest 過的文件在重新上傳後從 RAG 檢索中消失且無法恢復；保留舊向量、
        只記一筆 log 提醒「內容已更新但向量未同步」，比靜默刪除更安全。

        回傳 False 表示目標文件已不存在（呼叫端應改為新增）。
        """
        existing = await self.get_document_by_id(document_id)
        if not existing:
            return False

        stale_embeddings = await self.db.scalar(
            select(func.count(Embedding.id)).where(Embedding.document_id == document_id)
        )
        if stale_embeddings:
            logger.warning(
                f"Document {document_id} replaced with new content but its "
                f"{stale_embeddings} existing embedding(s) were left untouched "
                "(no reusable chunk+embed function outside /api/ingest) — "
                "RAG retrieval for this document may now be stale until re-ingested."
            )

        from sqlalchemy import update

        update_fields = {
            'title': document_data['title'],
            'content': document_data['content'],
            'subject': document_data['subject'],
            'grade': document_data.get('grade'),
            'chapter': document_data['chapter'],
            'page_number': document_data.get('page_number'),
            'image_filename': document_data.get('image_filename'),
            'source_filename': document_data.get('source_filename'),
        }
        await self.db.execute(
            update(Document).where(Document.id == document_id).values(**update_fields)
        )
        await self.db.commit()
        logger.info(f"Replaced document {document_id} with new upload content")
        return True

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
            'source_filename': document.source_filename,
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
            search_conditions.append(
                or_(Document.grade == grade, Document.grade == 'ALL')
            )
        
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
            import_source=document_data.get('import_source', 'manual'),
            source_filename=document_data.get('source_filename')
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
            'source_filename': document.source_filename,
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
        for key in [
            'title', 'content', 'subject', 'grade', 'chapter', 'page_number',
            'image_filename', 'source_filename',
        ]:
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

    async def batch_delete_documents(
        self, document_ids: List[int], force: bool = False
    ) -> Dict[str, Any]:
        """批次刪除文件（逐筆走既有引用檢查，最後一次 commit）

        Args:
            document_ids: 要刪除的文件 ID 列表
            force: 是否強制刪除（同時刪除相關問題與嵌入向量）

        Returns:
            Dict 包含 success_count / failed_count / failed（[{id, reason}]）
        """
        from sqlalchemy import delete

        success_count = 0
        failed: List[Dict[str, Any]] = []

        for document_id in document_ids:
            document = await self.get_document_by_id(document_id)
            if not document:
                failed.append({'id': document_id, 'reason': '文件不存在'})
                continue

            references = await self.check_document_references(document_id)

            if references['has_references'] and not force:
                failed.append({
                    'id': document_id,
                    'reason': f"被 {references['questions']} 題、{references['embeddings']} 個向量引用"
                })
                continue

            try:
                # 強制刪除時先移除引用的問題與向量
                if force:
                    if references['questions'] > 0:
                        await self.db.execute(
                            delete(Question).where(Question.document_id == document_id)
                        )
                    if references['embeddings'] > 0:
                        await self.db.execute(
                            delete(Embedding).where(Embedding.document_id == document_id)
                        )

                await self.db.execute(
                    delete(Document).where(Document.id == document_id)
                )
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to delete document {document_id} in batch: {str(e)}")
                failed.append({'id': document_id, 'reason': str(e)})

        await self.db.commit()

        return {
            'success_count': success_count,
            'failed_count': len(failed),
            'failed': failed
        }

    async def copy_documents_to_grades(
        self, document_ids: list[int], target_grades: list[str]
    ) -> dict[str, Any]:
        """複製文件（含其 embeddings）到其他年級，讓該年級的 RAG 檢索立即可用。

        對每個 (document_id, target_grade) 組合，判斷邏輯見 plan_document_copies：
        目標年級與來源相同、或已存在正規化後完全相同（科目+年級+章節+標題+頁碼）
        的文件時略過；查無來源文件時也記一筆略過原因。其餘則新增一筆文件（複製
        title/subject/chapter/page_number/content/image_urls/image_filename/
        image_data/source_filename）並複製其全部 embeddings。

        注意：Document model 沒有 source_metadata 欄位（僅 Question 有），無法字面
        依原規格存 {"copied_from": ..., "copied_at": ...}；改以 import_source 記錄
        來源文件 id（例如 "copied_from_document_42"）作為複製來源的可追溯標記，
        新列的 created_at（server_default=now()）即為複製時間，不另外加欄位
        （本任務明確排除 schema 變更）。

        整個請求的所有寫入（新文件 + 對應 embeddings）在同一交易內完成：
        任何一步失敗即整批 rollback，不會留下部份複製的髒資料。
        """
        if not document_ids or not target_grades:
            return {"created_ids": [], "skipped_items": []}

        result = await self.db.execute(
            select(Document).where(Document.id.in_(document_ids))
        )
        source_documents = result.scalars().all()
        docs_by_id = {d.id: d for d in source_documents}

        docs_for_plan = [
            {
                "id": d.id, "subject": d.subject, "grade": d.grade,
                "chapter": d.chapter, "title": d.title, "page_number": d.page_number,
            }
            for d in source_documents
        ]

        # 只查詢「來源文件所屬科目 × 目標年級」的既有文件，避免整表掃描
        # 科目比對要與 _match_key 一致(正規化 + 小寫),否則 'Health' 與 'health' 會漏掉
        subject_keys = {
            s.lower()
            for d in source_documents
            for s in (d.subject or "", normalize_subject(d.subject) or "")
            if s
        }
        existing_rows: list[dict[str, Any]] = []
        if subject_keys:
            conditions = [
                and_(
                    func.lower(func.trim(Document.subject)).in_(sorted(subject_keys)),
                    Document.grade == grade,
                )
                for grade in target_grades
            ]
            existing_result = await self.db.execute(
                select(
                    Document.id, Document.subject, Document.grade,
                    Document.chapter, Document.title, Document.page_number,
                ).where(or_(*conditions))
            )
            existing_rows = [
                {
                    'id': r.id, 'subject': r.subject, 'grade': r.grade,
                    'chapter': r.chapter, 'title': r.title, 'page_number': r.page_number,
                }
                for r in existing_result
            ]

        to_create, skipped_items = plan_document_copies(
            existing_rows, docs_for_plan, target_grades
        )

        # 傳入的 document_ids 中查無此文件者，對每個目標年級各記一筆略過原因
        missing_ids = set(document_ids) - set(docs_by_id.keys())
        for missing_id in missing_ids:
            for grade in target_grades:
                skipped_items.append({
                    "document_id": missing_id, "grade": grade,
                    "reason": "document not found",
                })

        created_ids: list[int] = []
        try:
            for item in to_create:
                source = docs_by_id[item["source"]["id"]]
                grade = item["grade"]

                new_document = Document(
                    title=source.title,
                    content=source.content,
                    subject=source.subject,
                    grade=grade,
                    chapter=source.chapter,
                    page_number=source.page_number,
                    image_urls=(
                        list(source.image_urls) if source.image_urls is not None else None
                    ),
                    image_filename=source.image_filename,
                    image_data=source.image_data,
                    import_source=f"copied_from_document_{source.id}",
                    source_filename=source.source_filename,
                )
                self.db.add(new_document)
                await self.db.flush()  # 取得 new_document.id 供 embeddings 使用

                embeddings_result = await self.db.execute(
                    select(Embedding).where(Embedding.document_id == source.id)
                )
                for embedding in embeddings_result.scalars().all():
                    self.db.add(Embedding(
                        document_id=new_document.id,
                        slice_text=embedding.slice_text,
                        vector=embedding.vector,
                    ))

                created_ids.append(new_document.id)

            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise

        return {"created_ids": created_ids, "skipped_items": skipped_items}


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
                'subject': 'health',
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
        source_file: Optional[str] = None,
        sort: str = "chapter",
        skip: int = 0,
        limit: Optional[int] = None,
        page_from: Optional[int] = None,
        page_to: Optional[int] = None,
    ) -> Dict[str, Any]:
        """取得文件清單（limit 為 None 時回傳全部）

        page_from / page_to：記憶體樣本資料沒有 page_number，best-effort 比對
        parse_page_range 後的區間；解析不出頁碼的列在篩選生效時會被排除。
        """
        filtered_docs = self.documents.copy()

        if subject:
            filtered_docs = [d for d in filtered_docs if d['subject'] == subject]

        if grade:
            filtered_docs = [d for d in filtered_docs if d.get('grade') == grade]

        if chapter:
            filtered_docs = [d for d in filtered_docs if chapter.lower() in d['chapter'].lower()]

        if source_file:
            filtered_docs = [d for d in filtered_docs if d.get('source_filename') == source_file]

        if page_from is not None or page_to is not None:
            def _in_page_range(doc: Dict[str, Any]) -> bool:
                parsed = parse_page_range(doc.get('page_number'))
                if parsed is None:
                    return False
                start, end = parsed
                if page_from is not None and end < page_from:
                    return False
                if page_to is not None and start > page_to:
                    return False
                return True

            filtered_docs = [d for d in filtered_docs if _in_page_range(d)]

        if search_query:
            filtered_docs = [
                d for d in filtered_docs
                if search_query.lower() in d['title'].lower()
                or search_query.lower() in d['content'].lower()
            ]

        if sort == "newest":
            filtered_docs = sorted(filtered_docs, key=lambda d: d['created_at'], reverse=True)
        else:
            filtered_docs = sorted(
                filtered_docs,
                key=lambda d: (
                    d['subject'], grade_sort_key(d.get('grade')), chapter_sort_key(d.get('chapter'))
                )
            )

        total = len(filtered_docs)
        if limit:
            paginated_docs = filtered_docs[skip:skip + limit]
        else:
            paginated_docs = filtered_docs[skip:]

        return {
            'documents': paginated_docs,
            'total': total,
            'page': (skip // limit) + 1 if limit else 1,
            'size': limit if limit else total,
            'pages': (total + limit - 1) // limit if limit else 1
        }

    async def get_document_stats(self) -> Dict[str, Any]:
        return {
            'total_documents': len(self.documents),
            'subjects': {'health': len(self.documents)},
            'top_chapters': {f'Chapter {i}': 1 for i in range(1, 6)},
            'has_images': len([d for d in self.documents if d['image_filename']])
        }

    async def batch_delete_documents(
        self, document_ids: List[int], force: bool = False
    ) -> Dict[str, Any]:
        """Mock 批次刪除：直接回報全部成功"""
        return {
            'success_count': len(document_ids),
            'failed_count': 0,
            'failed': []
        }

    async def delete_documents_by_source(
        self,
        source_filename: str,
        force: bool = False,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mock 依來源檔名刪除：記憶體樣本資料無 source_filename，固定回傳零筆"""
        return {
            'total': 0,
            'success_count': 0,
            'failed_count': 0,
            'failed': [],
            'source_filename': source_filename,
        }

    async def copy_documents_to_grades(
        self, document_ids: list[int], target_grades: list[str]
    ) -> dict[str, Any]:
        """Mock 複製：對記憶體樣本資料套用與真實模式相同的略過規則，不持久化寫入。"""
        if not document_ids or not target_grades:
            return {"created_ids": [], "skipped_items": []}

        docs_by_id = {d['id']: d for d in self.documents}
        docs_for_plan = [
            {
                "id": d["id"], "subject": d["subject"], "grade": d.get("grade"),
                "chapter": d.get("chapter"), "title": d.get("title"),
                "page_number": d.get("page_number"),
            }
            for d in self.documents if d["id"] in document_ids
        ]
        existing_rows = [
            {
                "id": d["id"], "subject": d["subject"], "grade": d.get("grade"),
                "chapter": d.get("chapter"), "title": d.get("title"),
                "page_number": d.get("page_number"),
            }
            for d in self.documents
        ]

        to_create, skipped_items = plan_document_copies(existing_rows, docs_for_plan, target_grades)

        missing_ids = set(document_ids) - set(docs_by_id.keys())
        for missing_id in missing_ids:
            for grade in target_grades:
                skipped_items.append({
                    "document_id": missing_id, "grade": grade,
                    "reason": "document not found",
                })

        # Mock 模式不持久化，僅回傳佔位 id 供前端驗證回應結構
        created_ids = [9000 + i for i in range(len(to_create))]
        return {"created_ids": created_ids, "skipped_items": skipped_items}