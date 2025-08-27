from typing import Optional, List
from pydantic import BaseModel, Field, validator
from .question import Subject

class IngestRequest(BaseModel):
    subject: Subject
    text: str = Field(..., min_length=3, max_length=100000, description="文件內容")
    title: Optional[str] = Field(None, max_length=200, description="文件標題")
    
    @validator('text')
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
