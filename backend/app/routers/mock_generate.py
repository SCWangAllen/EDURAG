from fastapi import APIRouter
from typing import List
from app.schemas.question import (
    GenerateRequest, 
    GenerateResponse, 
    QuestionItem, 
    QuestionType, 
    QuestionSource
)

router = APIRouter(prefix="/api/generate", tags=["mock", "generate"])

@router.post("/", response_model=GenerateResponse)
async def mock_generate(req: GenerateRequest):
    """Mock題目生成API，回傳與真實API相同的Schema"""
    
    questions_to_return: List[QuestionItem] = []
    
    # 為每種題型生成對應數量的模擬題目
    for question_type, count in req.types.items():
        for i in range(count):
            mock_question = _create_mock_question(question_type, i + 1, req.subject.value, req.document_id)
            questions_to_return.append(mock_question)
    
    return GenerateResponse(
        items=questions_to_return,
        total_count=len(questions_to_return),
        generation_time=0.8
    )

def _create_mock_question(question_type: QuestionType, index: int, subject: str, document_id: int) -> QuestionItem:
    """建立單個模擬題目"""
    
    mock_data = {
        QuestionType.SINGLE_CHOICE: {
            "prompt": f"[{index}] 根據{subject}課文內容，下列何者正確？",
            "options": ["A. 選項一", "B. 選項二", "C. 正確選項", "D. 選項四"],
            "answer": "C",
            "explanation": "根據課文內容分析，選項C為正確答案。"
        },
        QuestionType.CLOZE: {
            "prompt": f"[{index}] 請填入適當的詞語：課文中提到____是{subject}的重要概念。",
            "options": None,
            "answer": "知識",
            "explanation": "從上下文脈絡可以推斷出應填入「知識」一詞。"
        },
        QuestionType.SHORT_ANSWER: {
            "prompt": f"[{index}] 請簡述{subject}課文的主要觀點。",
            "options": None,
            "answer": f"{subject}課文主要強調學習的重要性以及持續進步的價值。",
            "explanation": "此答案涵蓋了課文的核心思想和主要論點。"
        }
    }
    
    question_data = mock_data[question_type]
    
    return QuestionItem(
        type=question_type,
        prompt=question_data["prompt"],
        options=question_data["options"],
        answer=question_data["answer"],
        explanation=question_data["explanation"],
        source=QuestionSource(
            document_id=document_id,
            chunk_id=1001 + index,
            chunk_text=f"這是來源文本塊 {index}，包含與題目相關的課文內容..."
        )
    )
