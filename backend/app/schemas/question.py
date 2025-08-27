from typing import List, Optional, Dict
from pydantic import BaseModel, Field, validator
from enum import Enum

class QuestionType(str, Enum):
    SINGLE_CHOICE = "single_choice"
    CLOZE = "cloze"
    SHORT_ANSWER = "short_answer"

class Subject(str, Enum):
    CHINESE = "chinese"
    ENGLISH = "english"
    MATH = "math"

class QuestionSource(BaseModel):
    document_id: int
    chunk_id: int
    chunk_text: str

class QuestionItem(BaseModel):
    type: QuestionType
    prompt: str = Field(..., description="題目題幹")
    options: Optional[List[str]] = Field(None, description="選項（單選題用）")
    answer: str = Field(..., description="答案")
    explanation: str = Field(..., description="解釋")
    source: QuestionSource = Field(..., description="來源文件與段落")

class GenerateRequest(BaseModel):
    subject: Subject
    document_id: int
    types: Dict[QuestionType, int] = Field(
        ..., 
        description="題型與數量映射",
        example={"single_choice": 3, "cloze": 2, "short_answer": 1}
    )
    
    @validator('types')
    def validate_types_not_empty(cls, v):
        if not v or all(count <= 0 for count in v.values()):
            raise ValueError('至少需要指定一種題型且數量大於0')
        return v

class GenerateResponse(BaseModel):
    items: List[QuestionItem]
    total_count: int
    generation_time: float = Field(..., description="生成耗時（秒）")
