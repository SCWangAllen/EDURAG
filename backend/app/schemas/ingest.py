from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from app.core.subject_norm import normalize_subject

class IngestRequest(BaseModel):
    subject: str = Field(..., min_length=1, max_length=50)
    text: str = Field(..., min_length=3, max_length=100000, description="文件內容")
    title: Optional[str] = Field(None, max_length=200, description="文件標題")

    @field_validator('subject')
    @classmethod
    def normalize_subject_value(cls, v):
        return normalize_subject(v)

    @field_validator('text')
    @classmethod
    def validate_text_content(cls, v):
        if not v.strip():
            raise ValueError('文件內容不能為空')
        return v.strip()

class ChunkInfo(BaseModel):
    chunk_id: int
    text: str
    token_count: int

class IngestResponse(BaseModel):
    document_id: int
    chunks: List[ChunkInfo]
    total_chunks: int
    processing_time: float = Field(..., description="處理耗時（秒）")
