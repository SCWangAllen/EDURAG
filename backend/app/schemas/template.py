from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class TemplateBase(BaseModel):
    subject_id: Optional[int] = Field(None, description="科目ID")
    subject: Optional[str] = Field(None, description="科目（兼容性）")
    name: str = Field(..., max_length=100, description="模板名稱")
    content: str = Field(..., description="Prompt 模板內容")
    params: Optional[Dict[str, Any]] = Field(None, description="LLM 參數設定")

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    subject_id: Optional[int] = Field(None, description="科目ID")
    name: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = Field(None)
    params: Optional[Dict[str, Any]] = Field(None)
    is_active: Optional[bool] = Field(None, description="是否啟用")

class TemplateResponse(BaseModel):
    id: int
    subject_id: Optional[int]
    subject: str  # 科目名稱（從關聯或舊欄位取得）
    name: str
    content: str
    params: Optional[Dict[str, Any]]
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TemplateList(BaseModel):
    templates: list[TemplateResponse]
    total: int
    page: int
    size: int

# 預設模板配置
DEFAULT_TEMPLATES = {
    "健康": {
        "單選題": {
            "content": """請根據以下健康教育文章內容，生成一道單選題。

文章內容：
{context}

請生成一道關於健康知識的單選題，包含：
1. 題幹：清楚的問題描述
2. 四個選項：A、B、C、D
3. 正確答案：明確指出正確選項
4. 解釋：說明為何此選項正確

格式要求：
- 題幹要具體明確，與健康知識相關
- 選項要合理且有辨識度
- 解釋要簡潔清楚，有助於學習

請以 JSON 格式回答：
{{"stem": "題幹", "options": ["A選項", "B選項", "C選項", "D選項"], "answer": "正確選項字母", "explanation": "解釋"}}""",
            "params": {"temperature": 0.7, "max_tokens": 500}
        }
    },
    "英文": {
        "單選題": {
            "content": """Based on the following English passage, create a multiple-choice question.

Passage:
{context}

Please generate a multiple-choice question about this English passage, including:
1. Question stem: Clear question description
2. Four options: A, B, C, D
3. Correct answer: Clearly indicate the correct option
4. Explanation: Explain why this option is correct

Requirements:
- The question stem should be specific and clear, related to English learning
- Options should be reasonable and distinguishable
- Explanation should be concise and clear for educational purposes

Please respond in JSON format:
{{"stem": "Question stem", "options": ["Option A", "Option B", "Option C", "Option D"], "answer": "Correct option letter", "explanation": "Explanation"}}""",
            "params": {"temperature": 0.7, "max_tokens": 500}
        }
    },
    "歷史": {
        "單選題": {
            "content": """請根據以下歷史文章內容，生成一道單選題。

文章內容：
{context}

請生成一道關於歷史知識的單選題，包含：
1. 題幹：清楚的問題描述
2. 四個選項：A、B、C、D
3. 正確答案：明確指出正確選項
4. 解釋：說明為何此選項正確

格式要求：
- 題幹要具體明確，與歷史事件或人物相關
- 選項要合理且有辨識度
- 解釋要簡潔清楚，提供歷史背景

請以 JSON 格式回答：
{{"stem": "題幹", "options": ["A選項", "B選項", "C選項", "D選項"], "answer": "正確選項字母", "explanation": "解釋"}}""",
            "params": {"temperature": 0.7, "max_tokens": 500}
        }
    }
}