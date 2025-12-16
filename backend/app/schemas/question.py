from typing import List, Optional, Dict, Union
from pydantic import BaseModel, Field, validator
from enum import Enum

class QuestionType(str, Enum):
    SINGLE_CHOICE = "single_choice"
    CLOZE = "cloze"
    SHORT_ANSWER = "short_answer"
    # G1~G2 新增題型
    TRUE_FALSE = "true_false"
    MATCHING = "matching"
    SEQUENCE = "sequence" 
    ENUMERATION = "enumeration"
    SYMBOL_IDENTIFICATION = "symbol_identification"
    # 系統題型
    MIXED = "mixed"  # 由模板自動判斷題型
    AUTO = "auto"    # 根據模板內容自動決定

class Subject(str, Enum):
    HEALTH = "health"
    ENGLISH = "english"
    HISTORY = "history"

# 題型特定資料結構
class MatchingQuestionData(BaseModel):
    """配對題專用資料"""
    left_items: List[str] = Field(..., description="左側配對項目")
    right_items: List[str] = Field(..., description="右側配對項目")

class SequenceQuestionData(BaseModel):
    """排序題專用資料"""  
    items: List[str] = Field(..., description="待排序項目")

class EnumerationQuestionData(BaseModel):
    """列舉題專用資料"""
    category: str = Field(..., description="列舉類別")
    min_items: int = Field(default=2, description="最少項目數")
    max_items: int = Field(default=8, description="最多項目數")

class SymbolIdentificationQuestionData(BaseModel):
    """符號識別題專用資料"""
    symbol_description: str = Field(..., description="符號文字描述")
    symbol_context: str = Field(..., description="符號使用情境")

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
    question_data: Optional[Dict] = Field(None, description="題型專用資料（配對項、排序項等）")

# 單個生成請求（擴展以支援模板驅動）
class SingleGenerateRequest(BaseModel):
    document_ids: List[int] = Field(..., description="文件ID列表")
    template_id: int = Field(..., description="模板ID")
    question_type: QuestionType = Field(default=QuestionType.AUTO, description="題目類型，AUTO表示由模板自動決定")
    count: int = Field(..., ge=1, le=20, description="生成數量")

# 新的模板驅動生成請求
class TemplateGenerateRequest(BaseModel):
    """基於模板的題目生成請求"""
    document_ids: List[int] = Field(..., description="文件ID列表")
    template_id: int = Field(..., description="模板ID")
    count: int = Field(default=1, ge=1, le=20, description="生成數量")
    # 不需要指定 question_type，由模板內容決定

# Prompt 驅動生成請求（最靈活的方式）
class PromptGenerateRequest(BaseModel):
    """基於完整 prompt 的題目生成請求"""
    prompt: str = Field(..., min_length=10, description="完整的生成提示")
    question_type: Optional[QuestionType] = Field(None, description="期望的題型，為空則自動判斷")
    count: int = Field(default=1, ge=1, le=20, description="生成數量")
    # LLM 參數
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=16384, ge=100, le=16384)
    model: str = Field(default="claude-3-7-sonnet-20250219", description="使用的模型")

# 完整模板驅動生成請求（包含模板資訊和文件內容）
class TemplateEnhancedGenerateRequest(BaseModel):
    """基於完整模板資訊的題目生成請求"""
    template: Dict = Field(..., description="完整的模板資訊，包含id, name, content, params等")
    documents: List[Dict] = Field(..., description="文件清單，包含id, title, content等")
    count: int = Field(default=1, ge=1, le=20, description="生成數量")
    question_type: Optional[QuestionType] = Field(None, description="期望的題型，為空則由模板決定")
    # 這些參數會被模板的params覆蓋
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="溫度（會被模板params覆蓋）")
    max_tokens: Optional[int] = Field(None, ge=100, le=16384, description="最大token數（會被模板params覆蓋）")
    model: str = Field(default="claude-3-7-sonnet-20250219", description="使用的模型")

# 批次模板生成請求
class BatchTemplateGenerateRequest(BaseModel):
    """批次模板驅動生成請求"""
    generations: List[TemplateGenerateRequest] = Field(
        ..., 
        description="模板生成請求列表",
        min_items=1
    )

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

# 批次生成請求
class BatchGenerateRequest(BaseModel):
    generations: List[SingleGenerateRequest] = Field(
        ..., 
        description="批次生成請求列表",
        min_items=1
    )
    
    @validator('generations')
    def validate_generations_not_empty(cls, v):
        if not v:
            raise ValueError('至少需要一個生成請求')
        return v

class GenerateResponse(BaseModel):
    items: List[QuestionItem]
    total_count: int
    generation_time: float = Field(..., description="生成耗時（秒）")

# 單個生成結果
class SingleGenerateResponse(BaseModel):
    question_type: QuestionType
    template_id: int
    items: List[QuestionItem]
    count: int
    generation_time: float

# 模板驅動生成結果
class TemplateGenerateResponse(BaseModel):
    template_id: int
    template_name: Optional[str] = None
    detected_question_types: List[QuestionType] = Field(default_factory=list, description="檢測到的題型")
    items: List[QuestionItem]
    count: int
    generation_time: float

# Prompt 驅動生成結果  
class PromptGenerateResponse(BaseModel):
    prompt: str
    detected_question_type: Optional[QuestionType] = None
    items: List[QuestionItem]
    count: int
    generation_time: float
    model_used: str
    tokens_used: Optional[int] = None

# 完整模板驅動生成結果
class TemplateEnhancedGenerateResponse(BaseModel):
    template_info: Dict = Field(..., description="使用的模板資訊")
    documents_info: List[Dict] = Field(..., description="使用的文件資訊")
    detected_question_type: Optional[QuestionType] = None
    items: List[QuestionItem]
    count: int
    generation_time: float
    model_used: str
    params_used: Dict = Field(..., description="實際使用的生成參數")
    warning: Optional[str] = Field(None, description="警告訊息（例如：使用了 fallback 題目）")
    is_fallback: bool = Field(default=False, description="是否使用了備用題目")

# 批次模板生成結果
class BatchTemplateGenerateResponse(BaseModel):
    results: List[TemplateGenerateResponse]
    total_items: int
    total_time: float
    success_count: int
    error_count: int
    errors: List[str] = []

# 批次生成回應
class BatchGenerateResponse(BaseModel):
    results: List[SingleGenerateResponse]
    total_items: int
    total_time: float
    success_count: int
    error_count: int
    errors: List[str] = []


# 問題管理相關模型
from datetime import datetime

class QuestionBase(BaseModel):
    type: str
    content: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    source_document_id: Optional[int] = None
    source_content: Optional[str] = None
    subject: Optional[str] = None
    chapter: Optional[str] = None
    grade: Optional[str] = None  # 年級 (G1-G6, ALL)
    difficulty: str = "medium"


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    type: Optional[str] = None
    content: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    subject: Optional[str] = None
    chapter: Optional[str] = None
    grade: Optional[str] = None  # 年級 (G1-G6, ALL)
    difficulty: Optional[str] = None


class QuestionResponse(QuestionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuestionListResponse(BaseModel):
    questions: List[QuestionResponse]
    total: int
    page: int
    size: int
    pages: int


class QuestionStatsResponse(BaseModel):
    total_questions: int
    by_type: Dict[str, int]
    by_subject: Dict[str, int]
    by_difficulty: Dict[str, int]


class QuestionExportRequest(BaseModel):
    format: str = Field(..., description="導出格式：json, csv, xlsx")
    subject: Optional[str] = None
    question_type: Optional[str] = None
    grade: Optional[str] = None  # 年級篩選
    difficulty: Optional[str] = None
