"""圖片題目管理服務"""
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text
from pathlib import Path
from io import BytesIO
import pandas as pd
import uuid
import logging
import re

from app.db.models import ImageQuestion
from app.schemas.image_question import (
    ImageQuestionCreate,
    ImageQuestionUpdate,
    ImageQuestionResponse,
    ImageQuestionListResponse,
    ImageQuestionStatsResponse,
    ImageQuestionPreviewItem,
    ImageUploadPreview,
    ImageVerifyResponse,
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

            question_image = str(row.get('question_image', '')).strip()
            answer_image = str(row.get('answer_image', '')).strip() if pd.notna(row.get('answer_image')) else None
            subject = str(row.get('subject', '')).strip()

            # 基本驗證
            has_error = False
            error_message = None

            if not question_image or question_image == 'nan':
                has_error = True
                error_message = "問題圖片名稱不能為空"
            elif not subject or subject == 'nan':
                has_error = True
                error_message = "科目不能為空"

            # 檢查圖片是否存在
            question_image_exists = self._check_image_exists(question_image, is_answer=False) if question_image else False
            answer_image_exists = self._check_image_exists(answer_image, is_answer=True) if answer_image else False

            if not question_image_exists and not has_error:
                warnings.append(f"第 {row_num} 行：問題圖片 '{question_image}' 不存在")

            if answer_image and not answer_image_exists:
                warnings.append(f"第 {row_num} 行：答案圖片 '{answer_image}' 不存在")

            item = ImageQuestionPreviewItem(
                row_number=row_num,
                question_image=question_image if question_image != 'nan' else '',
                answer_image=answer_image if answer_image and answer_image != 'nan' else None,
                question_description=str(row.get('question_description', '')).strip() if pd.notna(row.get('question_description')) else None,
                subject=subject if subject != 'nan' else '',
                chapter=str(row.get('chapter', '')).strip() if pd.notna(row.get('chapter')) else None,
                grade=str(row.get('grade', '')).strip() if pd.notna(row.get('grade')) else None,
                page=str(row.get('page', '')).strip() if pd.notna(row.get('page')) else None,
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
            total_rows=len(items),
            valid_rows=valid_count,
            error_rows=error_count,
            items=items,
            warnings=warnings,
        )

    async def create_batch(
        self,
        items: List[ImageQuestionPreviewItem],
        batch_id: Optional[str] = None,
        subject_service: Optional["SubjectService"] = None,
    ) -> int:
        """批次建立圖片題目

        Args:
            items: 預覽項目列表
            batch_id: 批次 ID
            subject_service: 可選的科目服務，用於自動創建科目

        Returns:
            創建的題目數量
        """
        if not batch_id:
            batch_id = str(uuid.uuid4())[:8]

        created_subjects = set()
        created_count = 0

        for item in items:
            if item.has_error:
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
        search: Optional[str] = None,
    ) -> ImageQuestionListResponse:
        """取得圖片題目清單"""
        conditions = [ImageQuestion.is_active == True]

        if subject:
            conditions.append(ImageQuestion.subject == subject)
        if grade:
            conditions.append(ImageQuestion.grade == grade)
        if chapter:
            conditions.append(ImageQuestion.chapter.ilike(f"%{chapter}%"))
        if verified is not None:
            conditions.append(ImageQuestion.images_verified == verified)
        if search:
            conditions.append(
                ImageQuestion.question_description.ilike(f"%{search}%") |
                ImageQuestion.question_image.ilike(f"%{search}%")
            )

        # 查詢總數
        count_stmt = select(func.count(ImageQuestion.id)).where(and_(*conditions))
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()

        # 查詢資料
        stmt = (
            select(ImageQuestion)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(ImageQuestion.created_at.desc())
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
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        self._next_id += 1
        self.mock_questions.append(new_question)
        return ImageQuestionResponse(**new_question)

    async def get_questions(self, **kwargs) -> ImageQuestionListResponse:
        return ImageQuestionListResponse(
            questions=self.mock_questions,
            total=len(self.mock_questions),
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
            total_rows=0,
            valid_rows=0,
            error_rows=0,
            items=[],
            warnings=["Mock mode: Excel parsing not available"],
        )

    async def create_batch(self, items: List[ImageQuestionPreviewItem], batch_id: Optional[str] = None) -> int:
        return 0

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
