"""圖片題目管理服務"""
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text, case, cast, Integer
from pathlib import Path
from io import BytesIO
import pandas as pd
import uuid
import logging
import re

from app.core.image_names import normalize_image_name
from app.core.subject_norm import GRADE_SORT_INDEX, VALID_GRADES
from app.db.models import ImageQuestion
from app.routers import images as images_router
from app.schemas.image_question import (
    ImageQuestionCreate,
    ImageQuestionUpdate,
    ImageQuestionResponse,
    ImageQuestionListResponse,
    ImageQuestionStatsResponse,
    ImageQuestionPreviewItem,
    ImageUploadPreview,
    ImageVerifyResponse,
    ImportBatchItem,
    ImportBatchListResponse,
    MissingImageItem,
    MissingImagesResponse,
)
from app.schemas.subject import SubjectCreate
from app.core.config import QUESTION_IMAGES_DIR, ANSWER_IMAGES_DIR

if TYPE_CHECKING:
    from app.services.subject_service import SubjectService

logger = logging.getLogger(__name__)

# 圖片目錄路徑
QUESTION_IMAGES_PATH = Path(QUESTION_IMAGES_DIR)
ANSWER_IMAGES_PATH = Path(ANSWER_IMAGES_DIR)

# 圖片名稱驗證正則表達式（只允許字母、數字、底線、連字號）
IMAGE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]+$')


def mark_duplicates(items, existing_names) -> int:
    """把「資料庫已有同名 question_image」或「同一批內重複」的項目標成 is_duplicate,回傳數量。

    純函式,不觸 DB;錯誤列(has_error)不計。同名的第一筆保留,之後的算重複。
    """
    existing = set(existing_names or ())
    seen = set()
    count = 0
    for item in items:
        item.is_duplicate = False
        if item.has_error or not item.question_image:
            continue
        name = item.question_image
        if name in existing or name in seen:
            item.is_duplicate = True
            count += 1
        else:
            seen.add(name)
    return count


def plan_orphan_images(deleted_names: set, still_referenced: set) -> set:
    """算出刪除批次後「真的不再被任何啟用中題目引用」的圖片名稱,純函式,不觸 DB/檔案系統。

    Args:
        deleted_names: 被刪除題目引用過的圖片名稱(question_image 與 answer_image 皆含)
        still_referenced: 仍被其他啟用中題目引用的圖片名稱(同樣涵蓋兩個欄位)

    Returns:
        deleted_names 扣除 still_referenced 後的差集,即可安全刪除實體檔的圖片名稱
    """
    return {name for name in deleted_names if name and name not in still_referenced}


def parse_blank_count(value) -> tuple[int, Optional[str]]:
    """把 Excel 的 Blanks 欄位值解析成作答空格數,純函式,不觸 DB。

    缺漏(None/空字串/NaN)或非正整數一律視為 1;非正整數時額外回傳警告訊息
    (呼叫端需自行補上列號)。

    Returns:
        (blank_count, warning_reason):warning_reason 為 None 表示不需要警告。
    """
    if value is None:
        return 1, None
    if isinstance(value, float) and pd.isna(value):
        return 1, None
    text_value = str(value).strip()
    if not text_value or text_value.lower() == "nan":
        return 1, None
    try:
        parsed = int(float(text_value))
    except (TypeError, ValueError):
        return 1, "不是正整數"
    if parsed < 1:
        return 1, "不是正整數"
    return parsed, None


class ImageQuestionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _ensure_subject_exists(
        self, subject_service: "SubjectService", subject_name: str
    ) -> bool:
        """確保科目存在，若不存在則自動創建

        Args:
            subject_service: 科目服務實例
            subject_name: 科目名稱

        Returns:
            True 表示科目已存在或成功創建
        """
        if not subject_name or not subject_name.strip():
            return False

        subject_name = subject_name.strip()

        try:
            existing = await subject_service.get_subject_by_name(subject_name)
            if existing:
                return True

            await subject_service.create_subject(SubjectCreate(
                name=subject_name,
                description=f"自動建立於圖片題目匯入",
                color="#3B82F6",
            ))
            logger.info(f"自動創建科目: {subject_name}")
            return True

        except ValueError as e:
            if "已存在" in str(e):
                return True
            logger.warning(f"創建科目失敗: {e}")
            return False
        except Exception as e:
            logger.error(f"確保科目存在時發生錯誤: {e}")
            return False

    async def create_single(
        self,
        data: ImageQuestionCreate,
        subject_service: Optional["SubjectService"] = None,
    ) -> ImageQuestionResponse:
        """創建單一圖片題目

        Args:
            data: 圖片題目創建資料
            subject_service: 可選的科目服務，用於自動創建科目

        Returns:
            創建的圖片題目
        """
        if subject_service and data.subject:
            await self._ensure_subject_exists(subject_service, data.subject)

        q_ext = self._find_image_extension(data.question_image, is_answer=False) or data.question_image_ext
        a_ext = self._find_image_extension(data.answer_image, is_answer=True) if data.answer_image else data.answer_image_ext

        question_image_exists = self._check_image_exists(data.question_image, is_answer=False)

        image_question = ImageQuestion(
            question_image=data.question_image,
            answer_image=data.answer_image,
            question_description=data.question_description,
            subject=data.subject,
            chapter=data.chapter,
            grade=data.grade,
            page=data.page,
            question_image_ext=q_ext,
            answer_image_ext=a_ext,
            images_verified=question_image_exists,
            import_batch_id=data.import_batch_id,
            blank_count=data.blank_count,
        )

        self.db.add(image_question)
        await self.db.commit()
        await self.db.refresh(image_question)

        logger.info(f"創建單一圖片題目: ID={image_question.id}")
        return self._to_response(image_question)

    def _validate_image_name(self, image_name: str) -> str:
        """驗證並清理圖片名稱，防止路徑穿越攻擊"""
        if not image_name:
            raise ValueError("圖片名稱不能為空")

        image_name = image_name.strip()

        # 檢查危險字元
        if ".." in image_name or "/" in image_name or "\\" in image_name:
            raise ValueError("圖片名稱包含無效字元")

        # 驗證名稱格式
        if not IMAGE_NAME_PATTERN.match(image_name):
            raise ValueError("圖片名稱只能包含字母、數字、底線和連字號")

        return image_name

    def _get_image_dir(self, is_answer: bool = False) -> Path:
        """取得圖片目錄路徑"""
        return ANSWER_IMAGES_PATH if is_answer else QUESTION_IMAGES_PATH

    def _get_name_variants(self, image_name: str, is_answer: bool = False) -> List[str]:
        """取得圖片名稱的可能變體（處理單底線/雙底線差異）

        例如：g4_answer_health -> [g4_answer_health, g4__answer__health]
        """
        variants = [image_name]

        if is_answer:
            # 嘗試將 _answer_ 轉換成 __answer__
            if '_answer_' in image_name and '__answer__' not in image_name:
                variants.append(image_name.replace('_answer_', '__answer__'))
            # 嘗試將 __answer__ 轉換成 _answer_
            elif '__answer__' in image_name:
                variants.append(image_name.replace('__answer__', '_answer_'))

        return variants

    def _check_image_exists(self, image_name: str, ext: str = "jpg", is_answer: bool = False) -> bool:
        """檢查圖片是否存在

        Args:
            image_name: 圖片名稱（不含副檔名）
            ext: 預設副檔名
            is_answer: True 為答案圖片，False 為問題圖片
        """
        if not image_name:
            return False

        image_name = normalize_image_name(image_name)
        if not image_name:
            return False

        try:
            image_name = self._validate_image_name(image_name)
        except ValueError:
            return False

        image_dir = self._get_image_dir(is_answer)
        name_variants = self._get_name_variants(image_name, is_answer)

        # 嘗試多種常見副檔名和名稱變體
        extensions = [ext, "jpg", "jpeg", "png", "gif", "webp"]
        for name in name_variants:
            for extension in extensions:
                image_path = image_dir / f"{name}.{extension}"
                # 確保解析後的路徑在正確目錄內
                if image_path.exists():
                    try:
                        image_path.resolve().relative_to(image_dir.resolve())
                        return True
                    except ValueError:
                        continue
        return False

    def _find_image_extension(self, image_name: str, is_answer: bool = False) -> Optional[str]:
        """尋找圖片的實際副檔名

        Args:
            image_name: 圖片名稱（不含副檔名）
            is_answer: True 為答案圖片，False 為問題圖片
        """
        if not image_name:
            return None

        image_name = normalize_image_name(image_name)
        if not image_name:
            return None

        try:
            image_name = self._validate_image_name(image_name)
        except ValueError:
            return None

        image_dir = self._get_image_dir(is_answer)
        name_variants = self._get_name_variants(image_name, is_answer)

        extensions = ["jpg", "jpeg", "png", "gif", "webp"]
        for name in name_variants:
            for ext in extensions:
                image_path = image_dir / f"{name}.{ext}"
                if image_path.exists():
                    try:
                        image_path.resolve().relative_to(image_dir.resolve())
                        return ext
                    except ValueError:
                        continue
        return None

    def parse_excel(self, contents: bytes, filename: str) -> ImageUploadPreview:
        """解析 Excel 檔案"""
        df = pd.read_excel(BytesIO(contents))

        # 標準化欄位名稱（不分大小寫）
        column_mapping = {
            'q_image': 'question_image',
            'ans_image': 'answer_image',
            'question': 'question_description',
            'subject': 'subject',
            'chapter': 'chapter',
            'grade': 'grade',
            'page': 'page',
            'blanks': 'blank_count',
            'blank_count': 'blank_count',
            'blank count': 'blank_count',
            '空格數': 'blank_count',
        }

        df.columns = df.columns.str.lower().str.strip()
        df = df.rename(columns=column_mapping)

        # 驗證必要欄位
        required_columns = ['question_image', 'subject']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Excel 缺少必要欄位: {', '.join(missing_columns)}")

        items: List[ImageQuestionPreviewItem] = []
        warnings: List[str] = []
        valid_count = 0
        error_count = 0

        for idx, row in df.iterrows():
            row_num = idx + 2  # Excel 行號（從1開始，加上標題行）

            question_image_raw = str(row.get('question_image', '')).strip()
            if question_image_raw == 'nan':
                question_image_raw = ''
            answer_image_cell = row.get('answer_image')
            answer_image_raw = str(answer_image_cell).strip() if pd.notna(answer_image_cell) else None
            if answer_image_raw == 'nan':
                answer_image_raw = None
            subject = str(row.get('subject', '')).strip()
            if subject == 'nan':
                subject = ''

            # 正規化圖片名稱：Excel 只 strip(),但上傳端點會清理特殊字元/去除副檔名,
            # 兩邊規則不一致會讓同一張圖被判定成兩個不同名稱(見 app/core/image_names.py)
            question_image = normalize_image_name(question_image_raw)
            answer_image = normalize_image_name(answer_image_raw) if answer_image_raw else None

            if question_image_raw and question_image != question_image_raw:
                warnings.append(f"第 {row_num} 行：圖片名已正規化：{question_image_raw} → {question_image}")
            if answer_image_raw and answer_image != answer_image_raw:
                warnings.append(f"第 {row_num} 行：圖片名已正規化：{answer_image_raw} → {answer_image}")

            # 基本驗證
            has_error = False
            error_message = None

            if not question_image:
                has_error = True
                error_message = "問題圖片名稱不能為空"
            elif not subject:
                has_error = True
                error_message = "科目不能為空"

            # 檢查圖片是否存在
            question_image_exists = self._check_image_exists(question_image, is_answer=False) if question_image else False
            answer_image_exists = self._check_image_exists(answer_image, is_answer=True) if answer_image else False

            if not question_image_exists and not has_error:
                warnings.append(f"第 {row_num} 行：問題圖片 '{question_image}' 不存在")

            if answer_image and not answer_image_exists:
                warnings.append(f"第 {row_num} 行：答案圖片 '{answer_image}' 不存在")

            blank_count, blank_count_warning = parse_blank_count(row.get('blank_count'))
            if blank_count_warning:
                warnings.append(f"第 {row_num} 列 Blanks {blank_count_warning}，已視為 1")

            item = ImageQuestionPreviewItem(
                row_number=row_num,
                question_image=question_image,
                answer_image=answer_image,
                question_description=str(row.get('question_description', '')).strip() if pd.notna(row.get('question_description')) else None,
                subject=subject,
                chapter=str(row.get('chapter', '')).strip() if pd.notna(row.get('chapter')) else None,
                grade=str(row.get('grade', '')).strip() if pd.notna(row.get('grade')) else None,
                page=str(row.get('page', '')).strip() if pd.notna(row.get('page')) else None,
                blank_count=blank_count,
                question_image_exists=question_image_exists,
                answer_image_exists=answer_image_exists,
                has_error=has_error,
                error_message=error_message,
            )

            items.append(item)
            if has_error:
                error_count += 1
            else:
                valid_count += 1

        return ImageUploadPreview(
            file_name=filename,
            source_filename=filename,
            total_rows=len(items),
            valid_rows=valid_count,
            error_rows=error_count,
            items=items,
            warnings=warnings,
        )

    async def _existing_question_image_names(self) -> set:
        """啟用中題目的問題圖名(正規化後)。只看啟用中:刪掉整批後重新匯入同一份 Excel
        才不會被判成全部重複;正規化:舊資料可能還是 '..._image02.1' 這種寫法。"""
        result = await self.db.execute(
            select(ImageQuestion.question_image).where(ImageQuestion.is_active.is_(True))
        )
        return {normalize_image_name(name) for (name,) in result.all() if name}

    async def annotate_duplicates(self, preview) -> int:
        """把預覽裡「資料庫已有」或「檔案內重複」的列標成 is_duplicate,寫入 preview.duplicate_rows。"""
        existing = await self._existing_question_image_names()
        count = mark_duplicates(preview.items, existing)
        preview.duplicate_rows = count
        if count:
            preview.warnings.append(f"有 {count} 筆的題目圖片已存在(或檔案內重複),儲存時會略過")
        return count

    async def create_batch(
        self,
        items: List[ImageQuestionPreviewItem],
        batch_id: Optional[str] = None,
        subject_service: Optional["SubjectService"] = None,
        source_filename: Optional[str] = None,
    ) -> int:
        """批次建立圖片題目

        Args:
            items: 預覽項目列表
            batch_id: 批次 ID
            subject_service: 可選的科目服務，用於自動創建科目
            source_filename: 匯入來源 Excel 檔名，寫入每一列的 source_filename

        Returns:
            創建的題目數量
        """
        if not batch_id:
            batch_id = str(uuid.uuid4())[:8]

        created_subjects = set()
        created_count = 0

        # 防呆:呼叫端沒先 annotate_duplicates 時,這裡也擋一次(同名的只寫第一筆)
        if not any(getattr(i, "is_duplicate", False) for i in items):
            existing = await self._existing_question_image_names()
            mark_duplicates(items, existing)

        for item in items:
            if item.has_error or getattr(item, "is_duplicate", False):
                continue

            if subject_service and item.subject and item.subject not in created_subjects:
                await self._ensure_subject_exists(subject_service, item.subject)
                created_subjects.add(item.subject)

            q_ext = self._find_image_extension(item.question_image, is_answer=False) or "jpg"
            a_ext = self._find_image_extension(item.answer_image, is_answer=True) if item.answer_image else "jpg"

            image_question = ImageQuestion(
                question_image=item.question_image,
                answer_image=item.answer_image,
                question_description=item.question_description,
                subject=item.subject,
                chapter=item.chapter,
                grade=item.grade,
                page=item.page,
                question_image_ext=q_ext,
                answer_image_ext=a_ext,
                images_verified=item.question_image_exists,
                import_batch_id=batch_id,
                source_filename=source_filename,
                blank_count=item.blank_count,
            )
            self.db.add(image_question)
            created_count += 1

        await self.db.commit()
        logger.info(f"批次建立 {created_count} 筆圖片題目，批次 ID: {batch_id}")
        if created_subjects:
            logger.info(f"自動創建的科目: {', '.join(created_subjects)}")
        return created_count

    async def get_questions(
        self,
        skip: int = 0,
        limit: int = 20,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        chapter: Optional[str] = None,
        verified: Optional[bool] = None,
        import_batch_id: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> ImageQuestionListResponse:
        """取得圖片題目清單"""
        conditions = [ImageQuestion.is_active == True]

        if subject:
            conditions.append(ImageQuestion.subject == subject)
        if grade:
            # 'ALL' 為全年級通用，任何年級篩選皆命中
            conditions.append(
                or_(ImageQuestion.grade == grade, ImageQuestion.grade == 'ALL')
            )
        if chapter:
            conditions.append(ImageQuestion.chapter.ilike(f"%{chapter}%"))
        if verified is not None:
            conditions.append(ImageQuestion.images_verified == verified)
        if import_batch_id:
            conditions.append(ImageQuestion.import_batch_id == import_batch_id)
        if search:
            conditions.append(
                ImageQuestion.question_description.ilike(f"%{search}%") |
                ImageQuestion.question_image.ilike(f"%{search}%")
            )

        # 查詢總數
        count_stmt = select(func.count(ImageQuestion.id)).where(and_(*conditions))
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()

        # 排序:白名單映射(防注入),方向由 sort_dir 決定;檔名做 tie-break
        _sort_cols = {
            "created_at": ImageQuestion.created_at,
            "question_image": ImageQuestion.question_image,
            "subject": ImageQuestion.subject,
            "grade": ImageQuestion.grade,
        }
        if sort_by == "chapter":
            # 章節自然排序：從章節文字取出第一個數字（最多 9 位，避免超長數字 cast 成
            # Integer 時 overflow 觸發 500）；無數字排最後
            chapter_num = cast(func.substring(ImageQuestion.chapter, r'\d{1,9}'), Integer)
            if sort_dir == "asc":
                order_terms = [chapter_num.asc().nulls_last(), ImageQuestion.chapter.asc()]
            else:
                order_terms = [chapter_num.desc().nulls_last(), ImageQuestion.chapter.desc()]
        elif sort_by == "grade":
            # 年級依 band 唯一權威順序排序（ESL → 年級班 → 國中班 → ALL 最後），而非依
            # 字母排序（字母排序會讓 'JR4' 排在 'G4' 前面、'ALL' 排在最前面）
            grade_order = case(
                GRADE_SORT_INDEX, value=ImageQuestion.grade, else_=len(VALID_GRADES)
            )
            order_terms = [
                grade_order.asc() if sort_dir == "asc" else grade_order.desc()
            ]
        else:
            sort_col = _sort_cols.get(sort_by, ImageQuestion.created_at)
            order_terms = [sort_col.asc() if sort_dir == "asc" else sort_col.desc()]

        # 查詢資料
        stmt = (
            select(ImageQuestion)
            .where(and_(*conditions))
            .order_by(*order_terms, ImageQuestion.question_image.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        questions = result.scalars().all()

        pages = (total + limit - 1) // limit
        page = (skip // limit) + 1

        return ImageQuestionListResponse(
            questions=[self._to_response(q) for q in questions],
            total=total,
            page=page,
            size=limit,
            pages=pages,
        )

    async def get_question_by_id(self, question_id: int) -> Optional[ImageQuestionResponse]:
        """根據 ID 取得單一題目"""
        stmt = select(ImageQuestion).where(
            ImageQuestion.id == question_id,
            ImageQuestion.is_active == True,
        )
        result = await self.db.execute(stmt)
        question = result.scalar_one_or_none()
        return self._to_response(question) if question else None

    async def update_question(
        self, question_id: int, data: ImageQuestionUpdate
    ) -> Optional[ImageQuestionResponse]:
        """更新圖片題目"""
        stmt = select(ImageQuestion).where(ImageQuestion.id == question_id)
        result = await self.db.execute(stmt)
        question = result.scalar_one_or_none()

        if not question:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(question, field, value)

        await self.db.commit()
        await self.db.refresh(question)
        return self._to_response(question)

    async def delete_question(self, question_id: int) -> bool:
        """刪除圖片題目（軟刪除）"""
        stmt = select(ImageQuestion).where(ImageQuestion.id == question_id)
        result = await self.db.execute(stmt)
        question = result.scalar_one_or_none()

        if not question:
            return False

        question.is_active = False
        await self.db.commit()
        return True

    async def batch_delete(self, ids: List[int]) -> dict:
        """批次刪除(軟刪 is_active=False,與單筆刪除語意一致)"""
        success_count = 0
        failed_ids: List[int] = []
        for qid in ids:
            try:
                stmt = select(ImageQuestion).where(
                    ImageQuestion.id == qid, ImageQuestion.is_active == True
                )
                result = await self.db.execute(stmt)
                q = result.scalar_one_or_none()
                if q:
                    q.is_active = False
                    success_count += 1
                else:
                    failed_ids.append(qid)
            except Exception:
                failed_ids.append(qid)
        await self.db.commit()
        return {
            "success_count": success_count,
            "failed_count": len(failed_ids),
            "failed_ids": failed_ids,
        }

    async def batch_update_tags(
        self,
        ids: List[int],
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        chapter: Optional[str] = None,
    ) -> dict:
        """批次改標籤:只更新有提供的欄位(subject/grade/chapter),僅對啟用中的列生效"""
        success_count = 0
        failed_ids: List[int] = []
        for qid in ids:
            try:
                stmt = select(ImageQuestion).where(
                    ImageQuestion.id == qid, ImageQuestion.is_active == True
                )
                result = await self.db.execute(stmt)
                q = result.scalar_one_or_none()
                if not q:
                    failed_ids.append(qid)
                    continue
                if subject is not None:
                    q.subject = subject
                if grade is not None:
                    q.grade = grade
                if chapter is not None:
                    q.chapter = chapter
                success_count += 1
            except Exception:
                failed_ids.append(qid)
        await self.db.commit()
        return {
            "success_count": success_count,
            "failed_count": len(failed_ids),
            "failed_ids": failed_ids,
        }

    async def list_import_batches(self) -> ImportBatchListResponse:
        """列出目前有啟用中題目的匯入批次,依匯入時間新到舊排序。

        imported_at 取該批次內最早的 created_at(同批次是同一次 create_batch
        呼叫、同一交易寫入,時間差可忽略);source_filename 取該批次內任一筆
        非 NULL 值(同批次理論上只會有一種來源檔名)。
        """
        verified_sum = func.coalesce(
            func.sum(cast(ImageQuestion.images_verified, Integer)), 0
        )
        stmt = (
            select(
                ImageQuestion.import_batch_id,
                func.max(ImageQuestion.source_filename),
                func.min(ImageQuestion.created_at),
                func.count(ImageQuestion.id),
                verified_sum,
            )
            .where(
                ImageQuestion.is_active.is_(True),
                ImageQuestion.import_batch_id.isnot(None),
            )
            .group_by(ImageQuestion.import_batch_id)
            .order_by(func.min(ImageQuestion.created_at).desc())
        )
        result = await self.db.execute(stmt)
        batches = []
        for batch_id, source_filename, imported_at, total, verified in result.all():
            verified = int(verified or 0)
            batches.append(
                ImportBatchItem(
                    batch_id=batch_id,
                    source_filename=source_filename,
                    imported_at=imported_at,
                    total=total,
                    verified=verified,
                    missing=total - verified,
                )
            )
        return ImportBatchListResponse(batches=batches)

    async def _active_image_names(self) -> set:
        """目前所有啟用中題目引用的圖片名稱集合(question_image 與 answer_image 皆含)。"""
        result = await self.db.execute(
            select(ImageQuestion.question_image, ImageQuestion.answer_image).where(
                ImageQuestion.is_active.is_(True)
            )
        )
        names: set = set()
        for question_image, answer_image in result.all():
            if question_image:
                names.add(question_image)
            if answer_image:
                names.add(answer_image)
        return names

    def _delete_image_files(self, name: str) -> bool:
        """在 questions/answers 兩個目錄嘗試刪除該圖名的所有支援格式檔案與其縮圖快取。

        圖名理論上只會落在其中一個目錄(question_image 存 questions、
        answer_image 存 answers),但同名巧合並非不可能,兩邊都嘗試較安全。
        回傳是否至少刪到一個檔案。
        """
        if not name or not IMAGE_NAME_PATTERN.match(name):
            # 舊資料可能存過未清理的字串;只允許 [A-Za-z0-9_-],杜絕路徑穿越
            logger.warning("略過不合法的圖名,不刪除檔案: %r", name)
            return False
        deleted_any = False
        for image_type in ("questions", "answers"):
            image_dir = images_router._get_image_dir(image_type)
            for ext in images_router.SUPPORTED_EXTENSIONS:
                file_path = image_dir / f"{name}.{ext}"
                if not file_path.exists():
                    continue
                try:
                    file_path.unlink()
                    images_router._remove_thumb_for(image_type, file_path)
                    deleted_any = True
                except OSError as e:
                    logger.warning(f"刪除孤兒圖片檔案失敗 {file_path}: {e}")
        return deleted_any

    async def delete_import_batch(
        self, batch_id: str, delete_orphan_images: bool = False
    ) -> Optional[dict]:
        """刪除整個匯入批次:軟刪其下所有啟用中題目,可選一併清除不再被引用的圖片檔。

        Returns:
            None 表示該批次沒有任何啟用中題目(呼叫端應回 404);
            否則回傳 {batch_id, deleted_questions, deleted_images, kept_images}
        """
        stmt = select(ImageQuestion).where(
            ImageQuestion.import_batch_id == batch_id,
            ImageQuestion.is_active.is_(True),
        )
        result = await self.db.execute(stmt)
        questions = result.scalars().all()
        if not questions:
            return None

        deleted_names: set = set()
        for q in questions:
            if q.question_image:
                deleted_names.add(q.question_image)
            if q.answer_image:
                deleted_names.add(q.answer_image)
            q.is_active = False

        await self.db.commit()

        deleted_images: list[str] = []
        if delete_orphan_images and deleted_names:
            still_referenced = await self._active_image_names()
            orphans = plan_orphan_images(deleted_names, still_referenced)
            for name in orphans:
                if self._delete_image_files(name):
                    deleted_images.append(name)
            kept_images = len(deleted_names) - len(orphans)
        else:
            kept_images = len(deleted_names)

        logger.info(
            f"刪除匯入批次 {batch_id}:軟刪 {len(questions)} 題,"
            f"清除孤兒圖片 {len(deleted_images)} 張,保留 {kept_images} 張"
        )

        return {
            "batch_id": batch_id,
            "deleted_questions": len(questions),
            "deleted_images": deleted_images,
            "kept_images": kept_images,
        }

    async def verify_images(self, question_ids: List[int]) -> ImageVerifyResponse:
        """驗證指定題目的圖片是否存在"""
        stmt = select(ImageQuestion).where(ImageQuestion.id.in_(question_ids))
        result = await self.db.execute(stmt)
        questions = result.scalars().all()

        results: Dict[int, Dict[str, bool]] = {}
        verified_count = 0
        failed_count = 0

        for question in questions:
            q_exists = self._check_image_exists(
                question.question_image, question.question_image_ext, is_answer=False
            )
            a_exists = True  # 預設為 True，除非有指定答案圖片
            if question.answer_image:
                a_exists = self._check_image_exists(
                    question.answer_image, question.answer_image_ext, is_answer=True
                )

            all_verified = q_exists and a_exists
            question.images_verified = all_verified

            results[question.id] = {
                "question_image": q_exists,
                "answer_image": a_exists,
            }

            if all_verified:
                verified_count += 1
            else:
                failed_count += 1

        await self.db.commit()

        return ImageVerifyResponse(
            total=len(questions),
            verified=verified_count,
            failed=failed_count,
            results=results,
        )

    async def get_stats(self) -> ImageQuestionStatsResponse:
        """取得統計資訊"""
        # 總數
        total_stmt = select(func.count(ImageQuestion.id)).where(
            ImageQuestion.is_active == True
        )
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar()

        # 已驗證數量
        verified_stmt = select(func.count(ImageQuestion.id)).where(
            ImageQuestion.is_active == True,
            ImageQuestion.images_verified == True,
        )
        verified_result = await self.db.execute(verified_stmt)
        verified_count = verified_result.scalar()

        # 按科目統計
        subject_stmt = (
            select(ImageQuestion.subject, func.count(ImageQuestion.id))
            .where(ImageQuestion.is_active == True)
            .group_by(ImageQuestion.subject)
        )
        subject_result = await self.db.execute(subject_stmt)
        by_subject = {row[0]: row[1] for row in subject_result.fetchall()}

        # 按年級統計
        grade_stmt = (
            select(ImageQuestion.grade, func.count(ImageQuestion.id))
            .where(ImageQuestion.is_active == True, ImageQuestion.grade.isnot(None))
            .group_by(ImageQuestion.grade)
        )
        grade_result = await self.db.execute(grade_stmt)
        by_grade = {row[0]: row[1] for row in grade_result.fetchall() if row[0]}

        # 按章節統計
        chapter_stmt = (
            select(ImageQuestion.chapter, func.count(ImageQuestion.id))
            .where(ImageQuestion.is_active == True, ImageQuestion.chapter.isnot(None))
            .group_by(ImageQuestion.chapter)
        )
        chapter_result = await self.db.execute(chapter_stmt)
        by_chapter = {row[0]: row[1] for row in chapter_result.fetchall() if row[0]}

        return ImageQuestionStatsResponse(
            total_questions=total,
            verified_count=verified_count,
            unverified_count=total - verified_count,
            by_subject=by_subject,
            by_grade=by_grade,
            by_chapter=by_chapter,
        )

    async def get_missing_images(self) -> MissingImagesResponse:
        """取得所有缺失圖片的題目清單

        返回格式包含:
        - missing_question_images: 問題圖片缺失的題目清單
        - missing_answer_images: 答案圖片缺失的題目清單
        - total_missing: 總缺失數量
        """
        # 查詢所有未驗證的題目
        stmt = select(ImageQuestion).where(
            ImageQuestion.is_active == True,
            ImageQuestion.images_verified == False,
        )
        result = await self.db.execute(stmt)
        unverified_questions = result.scalars().all()

        missing_question_images: List[MissingImageItem] = []
        missing_answer_images: List[MissingImageItem] = []

        for question in unverified_questions:
            # 檢查問題圖片是否存在
            q_exists = self._check_image_exists(
                question.question_image,
                question.question_image_ext,
                is_answer=False
            )
            if not q_exists:
                missing_question_images.append(MissingImageItem(
                    id=question.id,
                    image_name=question.question_image,
                    image_type="question",
                    subject=question.subject,
                    grade=question.grade,
                    chapter=question.chapter,
                ))

            # 檢查答案圖片是否存在（如果有指定）
            if question.answer_image:
                a_exists = self._check_image_exists(
                    question.answer_image,
                    question.answer_image_ext,
                    is_answer=True
                )
                if not a_exists:
                    missing_answer_images.append(MissingImageItem(
                        id=question.id,
                        image_name=question.answer_image,
                        image_type="answer",
                        subject=question.subject,
                        grade=question.grade,
                        chapter=question.chapter,
                    ))

        total_missing = len(missing_question_images) + len(missing_answer_images)

        return MissingImagesResponse(
            missing_question_images=missing_question_images,
            missing_answer_images=missing_answer_images,
            total_missing=total_missing,
        )

    def _to_response(self, question: ImageQuestion) -> ImageQuestionResponse:
        """轉換為回應 schema"""
        return ImageQuestionResponse(
            id=question.id,
            question_image=question.question_image,
            answer_image=question.answer_image,
            question_description=question.question_description,
            subject=question.subject,
            chapter=question.chapter,
            grade=question.grade,
            page=question.page,
            question_image_ext=question.question_image_ext,
            answer_image_ext=question.answer_image_ext,
            question_image_path=question.question_image_path,
            answer_image_path=question.answer_image_path,
            images_verified=question.images_verified,
            import_batch_id=question.import_batch_id,
            source_filename=question.source_filename,
            blank_count=question.blank_count,
            is_active=question.is_active,
            created_at=question.created_at,
            updated_at=question.updated_at,
        )


class MockImageQuestionService:
    """Mock 圖片題目服務"""

    def __init__(self):
        self._next_id = 3
        self.mock_questions = [
            {
                "id": 1,
                "question_image": "g4_question_health_v4_5_image01",
                "answer_image": "g4_answer_health_v4_5_image01",
                "question_description": "Look at the Picture and Fill in the Blanks",
                "subject": "Health",
                "chapter": "Chapter 2",
                "grade": "G4",
                "page": "5",
                "question_image_ext": "jpg",
                "answer_image_ext": "jpg",
                "question_image_path": "g4_question_health_v4_5_image01.jpg",
                "answer_image_path": "g4_answer_health_v4_5_image01.jpg",
                "images_verified": True,
                "import_batch_id": "mock001",
                "source_filename": "mock_import.xlsx",
                "blank_count": 1,
                "is_active": True,
                "created_at": "2026-02-21T10:00:00Z",
                "updated_at": "2026-02-21T10:00:00Z",
            },
            {
                "id": 2,
                "question_image": "g4_question_health_v4_5_image02",
                "answer_image": None,
                "question_description": "Identify the Body Parts",
                "subject": "Health",
                "chapter": "Chapter 3",
                "grade": "G4",
                "page": "8",
                "question_image_ext": "jpg",
                "answer_image_ext": "jpg",
                "question_image_path": "g4_question_health_v4_5_image02.jpg",
                "answer_image_path": None,
                "images_verified": False,
                "import_batch_id": "mock001",
                "source_filename": "mock_import.xlsx",
                "blank_count": 1,
                "is_active": True,
                "created_at": "2026-02-21T11:00:00Z",
                "updated_at": "2026-02-21T11:00:00Z",
            },
        ]

    async def create_single(self, data: ImageQuestionCreate) -> ImageQuestionResponse:
        """Mock 創建單一圖片題目"""
        from datetime import datetime
        now = datetime.now().isoformat() + "Z"

        new_question = {
            "id": self._next_id,
            "question_image": data.question_image,
            "answer_image": data.answer_image,
            "question_description": data.question_description,
            "subject": data.subject,
            "chapter": data.chapter,
            "grade": data.grade,
            "page": data.page,
            "question_image_ext": data.question_image_ext,
            "answer_image_ext": data.answer_image_ext,
            "question_image_path": f"{data.question_image}.{data.question_image_ext}",
            "answer_image_path": f"{data.answer_image}.{data.answer_image_ext}" if data.answer_image else None,
            "images_verified": False,
            "import_batch_id": data.import_batch_id or f"mock{self._next_id:03d}",
            "source_filename": None,
            "blank_count": data.blank_count,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        self._next_id += 1
        self.mock_questions.append(new_question)
        return ImageQuestionResponse(**new_question)

    async def get_questions(
        self, import_batch_id: Optional[str] = None, **kwargs
    ) -> ImageQuestionListResponse:
        questions = self.mock_questions
        if import_batch_id:
            questions = [q for q in questions if q.get("import_batch_id") == import_batch_id]
        return ImageQuestionListResponse(
            questions=questions,
            total=len(questions),
            page=1,
            size=20,
            pages=1,
        )

    async def get_question_by_id(self, question_id: int) -> Optional[Dict]:
        for q in self.mock_questions:
            if q["id"] == question_id:
                return q
        return None

    async def update_question(self, question_id: int, data: ImageQuestionUpdate) -> Optional[Dict]:
        for q in self.mock_questions:
            if q["id"] == question_id:
                update_data = data.model_dump(exclude_unset=True)
                q.update(update_data)
                return q
        return None

    async def delete_question(self, question_id: int) -> bool:
        for i, q in enumerate(self.mock_questions):
            if q["id"] == question_id:
                self.mock_questions.pop(i)
                return True
        return False

    async def batch_delete(self, ids: List[int]) -> dict:
        before = len(self.mock_questions)
        keep = [q for q in self.mock_questions if q["id"] not in set(ids)]
        self.mock_questions = keep
        success = before - len(keep)
        return {"success_count": success, "failed_count": len(ids) - success, "failed_ids": []}

    async def batch_update_tags(
        self, ids: List[int], subject=None, grade=None, chapter=None
    ) -> dict:
        idset = set(ids)
        success = 0
        for q in self.mock_questions:
            if q["id"] in idset:
                if subject is not None:
                    q["subject"] = subject
                if grade is not None:
                    q["grade"] = grade
                if chapter is not None:
                    q["chapter"] = chapter
                success += 1
        return {"success_count": success, "failed_count": len(ids) - success, "failed_ids": []}

    async def verify_images(self, question_ids: List[int]) -> ImageVerifyResponse:
        results = {}
        verified_count = 0
        for qid in question_ids:
            results[qid] = {"question_image": True, "answer_image": True}
            verified_count += 1
        return ImageVerifyResponse(
            total=len(question_ids),
            verified=verified_count,
            failed=0,
            results=results,
        )

    def parse_excel(self, contents: bytes, filename: str) -> ImageUploadPreview:
        return ImageUploadPreview(
            file_name=filename,
            source_filename=filename,
            total_rows=0,
            valid_rows=0,
            error_rows=0,
            items=[],
            warnings=["Mock mode: Excel parsing not available"],
        )

    async def create_batch(
        self,
        items: List[ImageQuestionPreviewItem],
        batch_id: Optional[str] = None,
        source_filename: Optional[str] = None,
    ) -> int:
        return 0

    async def annotate_duplicates(self, preview) -> int:
        """mock:沒有既有資料,只標檔案內重複。"""
        count = mark_duplicates(preview.items, set())
        preview.duplicate_rows = count
        return count

    async def list_import_batches(self) -> dict:
        """依 import_batch_id 分組出目前(mock 資料中)有效的匯入批次清單。"""
        groups: dict[str, list[dict]] = {}
        for q in self.mock_questions:
            if not q.get("is_active", True):
                continue
            batch_id = q.get("import_batch_id")
            if not batch_id:
                continue
            groups.setdefault(batch_id, []).append(q)

        batches = []
        for batch_id, qs in groups.items():
            verified = sum(1 for q in qs if q.get("images_verified"))
            source_filename = next(
                (q.get("source_filename") for q in qs if q.get("source_filename")), None
            )
            batches.append({
                "batch_id": batch_id,
                "source_filename": source_filename,
                "imported_at": min(q["created_at"] for q in qs),
                "total": len(qs),
                "verified": verified,
                "missing": len(qs) - verified,
            })
        batches.sort(key=lambda b: b["imported_at"], reverse=True)
        return {"batches": batches}

    async def delete_import_batch(
        self, batch_id: str, delete_orphan_images: bool = False
    ) -> Optional[dict]:
        """mock:軟刪該批次的啟用中題目;不觸碰檔案系統,deleted_images 恆為空。"""
        matching = [
            q for q in self.mock_questions
            if q.get("import_batch_id") == batch_id and q.get("is_active", True)
        ]
        if not matching:
            return None

        names: set = set()
        for q in matching:
            if q.get("question_image"):
                names.add(q["question_image"])
            if q.get("answer_image"):
                names.add(q["answer_image"])
            q["is_active"] = False

        return {
            "batch_id": batch_id,
            "deleted_questions": len(matching),
            "deleted_images": [],
            "kept_images": len(names),
        }

    async def get_stats(self) -> ImageQuestionStatsResponse:
        return ImageQuestionStatsResponse(
            total_questions=2,
            verified_count=1,
            unverified_count=1,
            by_subject={"Health": 2},
            by_grade={"G4": 2},
            by_chapter={"Chapter 2": 1, "Chapter 3": 1},
        )

    async def get_missing_images(self) -> MissingImagesResponse:
        """Mock 取得缺失圖片清單"""
        return MissingImagesResponse(
            missing_question_images=[
                MissingImageItem(
                    id=2,
                    image_name="g4_question_health_v4_5_image02",
                    image_type="question",
                    subject="Health",
                    grade="G4",
                    chapter="Chapter 3",
                )
            ],
            missing_answer_images=[],
            total_missing=1,
        )
