"""圖片題目相關的 Pydantic schemas"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

from app.core.image_names import normalize_image_name
from app.core.subject_norm import normalize_grade, normalize_subject


class ImageQuestionBase(BaseModel):
    """圖片題目基礎 schema"""

    question_image: str = Field(..., description="問題圖片名（不含副檔名）")
    answer_image: Optional[str] = Field(None, description="答案圖片名（不含副檔名）")
    question_description: Optional[str] = Field(None, description="題目類型描述")
    subject: str = Field(..., description="科目")
    chapter: Optional[str] = Field(None, description="章節")
    grade: Optional[str] = Field(None, description="年級代碼（見 GET /api/subjects/grades）")
    page: Optional[str] = Field(None, description="頁碼")
    question_image_ext: str = Field(default="jpg", description="問題圖片副檔名")
    answer_image_ext: str = Field(default="jpg", description="答案圖片副檔名")

    @field_validator("question_image")
    @classmethod
    def normalize_question_image_value(cls, v):
        normalized = normalize_image_name(v)
        if not normalized:
            raise ValueError("圖片名稱不可為空")
        return normalized

    @field_validator("answer_image")
    @classmethod
    def normalize_answer_image_value(cls, v):
        if v is None:
            return v
        return normalize_image_name(v) or None

    @field_validator("subject")
    @classmethod
    def normalize_subject_value(cls, v):
        return normalize_subject(v)

    @field_validator("grade")
    @classmethod
    def normalize_grade_value(cls, v):
        if v is None:
            return v
        return normalize_grade(v) or None


class ImageQuestionCreate(ImageQuestionBase):
    """建立圖片題目的 schema"""

    import_batch_id: Optional[str] = Field(None, description="匯入批次 ID")


class ImageQuestionUpdate(BaseModel):
    """更新圖片題目的 schema"""

    question_image: Optional[str] = None
    answer_image: Optional[str] = None
    question_description: Optional[str] = None
    subject: Optional[str] = None
    chapter: Optional[str] = None
    grade: Optional[str] = None
    page: Optional[str] = None
    question_image_ext: Optional[str] = None
    answer_image_ext: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("question_image")
    @classmethod
    def normalize_question_image_value(cls, v):
        if v is None:
            return v
        normalized = normalize_image_name(v)
        if not normalized:
            raise ValueError("圖片名稱不可為空")
        return normalized

    @field_validator("answer_image")
    @classmethod
    def normalize_answer_image_value(cls, v):
        if v is None:
            return v
        return normalize_image_name(v) or None

    @field_validator("subject")
    @classmethod
    def normalize_subject_value(cls, v):
        return normalize_subject(v) if v is not None else v

    @field_validator("grade")
    @classmethod
    def normalize_grade_value(cls, v):
        if v is None:
            return v
        return normalize_grade(v) or None


class ImageQuestionResponse(ImageQuestionBase):
    """圖片題目回應 schema"""

    id: int
    question_image_path: str = Field(..., description="問題圖片完整路徑")
    answer_image_path: Optional[str] = Field(None, description="答案圖片完整路徑")
    images_verified: bool = Field(default=False, description="圖片是否已驗證存在")
    import_batch_id: Optional[str] = None
    source_filename: Optional[str] = Field(None, description="匯入來源 Excel 檔名")
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ImageQuestionListResponse(BaseModel):
    """圖片題目清單回應 schema"""

    questions: List[ImageQuestionResponse]
    total: int
    page: int
    size: int
    pages: int


class ImageQuestionStatsResponse(BaseModel):
    """圖片題目統計回應 schema"""

    total_questions: int
    verified_count: int
    unverified_count: int
    by_subject: Dict[str, int]
    by_grade: Dict[str, int]
    by_chapter: Dict[str, int]


class ImageQuestionPreviewItem(BaseModel):
    """Excel 預覽項目"""

    row_number: int
    question_image: str
    answer_image: Optional[str] = None
    question_description: Optional[str] = None
    subject: str
    chapter: Optional[str] = None
    grade: Optional[str] = None
    page: Optional[str] = None
    question_image_exists: bool = False
    answer_image_exists: bool = False
    has_error: bool = False
    error_message: Optional[str] = None
    is_duplicate: bool = False  # 資料庫已有同名 question_image,或同一份檔案內重複;儲存時略過


class ImageUploadPreview(BaseModel):
    """Excel 上傳預覽結果"""

    file_name: str
    source_filename: Optional[str] = Field(
        None, description="上傳的 Excel 來源檔名(儲存時會寫入每一列的 source_filename)"
    )
    total_rows: int
    valid_rows: int
    error_rows: int
    items: List[ImageQuestionPreviewItem]
    warnings: List[str] = []
    duplicate_rows: int = 0  # 將被略過的重複列數
    saved_rows: int = 0  # 實際寫入筆數(preview_only=False 時)


class ImageVerifyRequest(BaseModel):
    """圖片驗證請求"""

    question_ids: List[int] = Field(..., description="要驗證的題目 ID 列表")


class ImageVerifyResponse(BaseModel):
    """圖片驗證結果"""

    total: int
    verified: int
    failed: int
    results: Dict[int, Dict[str, bool]] = Field(
        ..., description="每個題目的驗證結果 {id: {question_image: bool, answer_image: bool}}"
    )


class MissingImageItem(BaseModel):
    """缺失圖片項目"""

    id: int
    image_name: str = Field(..., description="缺失的圖片名稱")
    image_type: str = Field(..., description="圖片類型: question 或 answer")
    subject: str
    grade: Optional[str] = None
    chapter: Optional[str] = None


class MissingImagesResponse(BaseModel):
    """缺失圖片統計結果"""

    missing_question_images: List[MissingImageItem] = Field(
        default_factory=list, description="問題圖片缺失的題目清單"
    )
    missing_answer_images: List[MissingImageItem] = Field(
        default_factory=list, description="答案圖片缺失的題目清單"
    )
    total_missing: int = Field(default=0, description="總缺失圖片數量")


class ImageQuestionBatchDeleteRequest(BaseModel):
    """批次刪除請求"""

    ids: List[int] = Field(..., min_length=1, description="要刪除的圖片題目 ID 列表")


class ImageQuestionBatchUpdateRequest(BaseModel):
    """批次改標籤請求(只帶要更新的欄位;留空表示不改)"""

    ids: List[int] = Field(..., min_length=1, description="要更新的圖片題目 ID 列表")
    subject: Optional[str] = Field(None, description="科目")
    grade: Optional[str] = Field(None, description="年級")
    chapter: Optional[str] = Field(None, description="章節")


class ImageQuestionBatchResponse(BaseModel):
    """批次操作回應"""

    success_count: int = Field(..., description="成功處理的數量")
    failed_count: int = Field(..., description="失敗的數量")
    failed_ids: List[int] = Field(default_factory=list, description="失敗的 ID 列表")


class ImportBatchItem(BaseModel):
    """單一匯入批次摘要"""

    batch_id: str
    source_filename: Optional[str] = Field(None, description="匯入來源 Excel 檔名")
    imported_at: datetime = Field(..., description="批次匯入時間(取批次內最早的建立時間)")
    total: int = Field(..., description="此批次目前啟用中的題目數")
    verified: int = Field(..., description="已驗證圖片存在的題目數")
    missing: int = Field(..., description="圖片缺失的題目數（total - verified）")


class ImportBatchListResponse(BaseModel):
    """匯入批次清單回應"""

    batches: list[ImportBatchItem] = Field(default_factory=list)


class ImportBatchDeleteResponse(BaseModel):
    """刪除匯入批次回應"""

    batch_id: str
    deleted_questions: int = Field(..., description="被軟刪除的題目數")
    deleted_images: list[str] = Field(
        default_factory=list, description="一併刪除的孤兒圖片檔名列表(不含副檔名)"
    )
    kept_images: int = Field(..., description="被此批次引用但因仍被其他啟用中題目引用（或未要求刪除）而保留的圖片數")
