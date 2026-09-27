from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class DocumentBase(BaseModel):
    """文件基本欄位"""
    subject: str = Field(..., min_length=1, max_length=32, description="科目")
    title: Optional[str] = Field(None, max_length=200, description="文件標題")
    content: str = Field(..., min_length=1, description="文件內容")
    grade: Optional[str] = Field(None, max_length=50, description="適用年級（任意格式）")
    chapter: Optional[str] = Field(None, description="章節（不限長度）")
    page_number: Optional[str] = Field(None, max_length=20, description="頁碼")

    @validator('subject')
    def validate_subject(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('科目不能為空')
        return v

    @validator('content')
    def validate_content(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('文件內容不能為空')
        return v


class DocumentCreate(DocumentBase):
    """建立文件請求"""
    image_urls: Optional[List[str]] = None
    image_filename: Optional[str] = Field(None, max_length=255)
    image_data: Optional[str] = None
    import_source: str = Field(default='manual', max_length=100)


class DocumentUpdate(BaseModel):
    """更新文件請求"""
    subject: Optional[str] = Field(None, min_length=1, max_length=32)
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    grade: Optional[str] = None
    chapter: Optional[str] = Field(None)
    page_number: Optional[str] = Field(None, max_length=20)
    image_urls: Optional[List[str]] = None
    image_filename: Optional[str] = Field(None, max_length=255)
    image_data: Optional[str] = None

    @validator('subject')
    def validate_subject(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('科目不能為空')
        return v

    @validator('content')
    def validate_content(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('文件內容不能為空')
        return v


class DocumentResponse(BaseModel):
    """文件回應"""
    id: int
    subject: str
    title: Optional[str]
    content: str
    grade: Optional[str]
    chapter: Optional[str]
    page_number: Optional[str]
    image_urls: Optional[List[str]]
    image_filename: Optional[str]
    has_image: bool = False
    import_source: str
    source_filename: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DocumentsListResponse(BaseModel):
    """文件清單回應"""
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int


class DocumentSearchRequest(BaseModel):
    """文件搜尋請求"""
    query: Optional[str] = Field(None, description="搜尋關鍵字")
    subject: Optional[str] = Field(None, description="科目篩選")
    grade: Optional[str] = Field(None, description="年級篩選")
    chapter: Optional[str] = Field(None, description="章節篩選")
    page: int = Field(default=1, ge=1, description="頁碼")
    page_size: int = Field(default=20, ge=1, le=100, description="每頁數量")


class DocumentBatchDeleteRequest(BaseModel):
    """批次刪除文件請求"""
    document_ids: List[int] = Field(..., min_length=1, description="要刪除的文件 ID 列表")
    force: bool = Field(default=False, description="是否強制刪除（同時刪除相關問題與向量）")


class DocumentBatchDeleteFailure(BaseModel):
    """批次刪除失敗項目"""
    id: int
    reason: str


class DocumentBatchDeleteResponse(BaseModel):
    """批次刪除文件回應"""
    success_count: int = Field(..., description="成功刪除的數量")
    failed_count: int = Field(..., description="刪除失敗的數量")
    failed: List[DocumentBatchDeleteFailure] = Field(default=[], description="刪除失敗的項目與原因")
