"""圖片題目相關的 Pydantic schemas"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class ImageQuestionBase(BaseModel):
    """圖片題目基礎 schema"""
    question_image: str = Field(..., description="問題圖片名（不含副檔名）")
    answer_image: Optional[str] = Field(None, description="答案圖片名（不含副檔名）")
    question_description: Optional[str] = Field(None, description="題目類型描述")
    subject: str = Field(..., description="科目")
    chapter: Optional[str] = Field(None, description="章節")
    grade: Optional[str] = Field(None, description="年級 (G1-G6)")
    page: Optional[str] = Field(None, description="頁碼")
    question_image_ext: str = Field(default="jpg", description="問題圖片副檔名")
    answer_image_ext: str = Field(default="jpg", description="答案圖片副檔名")


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


class ImageQuestionResponse(ImageQuestionBase):
    """圖片題目回應 schema"""
    id: int
    question_image_path: str = Field(..., description="問題圖片完整路徑")
    answer_image_path: Optional[str] = Field(None, description="答案圖片完整路徑")
    images_verified: bool = Field(default=False, description="圖片是否已驗證存在")
    import_batch_id: Optional[str] = None
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


class ImageUploadPreview(BaseModel):
    """Excel 上傳預覽結果"""
    file_name: str
    total_rows: int
    valid_rows: int
    error_rows: int
    items: List[ImageQuestionPreviewItem]
    warnings: List[str] = []


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
