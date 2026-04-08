from fastapi import APIRouter
from typing import List
from app.schemas.question import (
    GenerateRequest, 
    GenerateResponse, 
    BatchGenerateRequest,
    BatchGenerateResponse,
    SingleGenerateResponse,
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

@router.post("/batch", response_model=BatchGenerateResponse)
async def mock_generate_batch(req: BatchGenerateRequest):
    """Mock批次題目生成API"""
    
    results = []
    total_items = 0
    success_count = 0
    
    # 處理每個生成請求
    for gen_req in req.generations:
        try:
            # 創建模擬題目
            questions = []
            for i in range(gen_req.count):
                mock_question = _create_mock_batch_question(
                    gen_req.question_type, 
                    i + 1, 
                    gen_req.template_id,
                    gen_req.document_ids[0] if gen_req.document_ids else 1
                )
                questions.append(mock_question)
            
            # 創建單個生成結果
            single_result = SingleGenerateResponse(
                question_type=gen_req.question_type,
                template_id=gen_req.template_id,
                items=questions,
                count=len(questions),
                generation_time=0.5
            )
            
            results.append(single_result)
            success_count += 1
            total_items += len(questions)
            
        except Exception as e:
            # 在實際應用中，這裡會記錄錯誤
            continue
    
    return BatchGenerateResponse(
        results=results,
        total_items=total_items,
        total_time=1.2,
        success_count=success_count,
        error_count=len(req.generations) - success_count,
        errors=[]
    )

def _create_mock_batch_question(question_type: QuestionType, index: int, template_id: int, document_id: int) -> QuestionItem:
    """為批次生成創建模擬題目"""
    
    template_subjects = {
        1: "健康",
        2: "英文", 
        3: "歷史"
    }
    
    subject = template_subjects.get(template_id, "一般")
    
    mock_data = {
        QuestionType.SINGLE_CHOICE: {
            "prompt": f"[模板{template_id}-{index}] 根據{subject}課文內容，下列何者正確？",
            "options": ["A. 選項一", "B. 選項二", "C. 正確選項", "D. 選項四"],
            "answer": "C",
            "explanation": f"根據{subject}課文內容分析，選項C為正確答案。"
        },
        QuestionType.CLOZE: {
            "prompt": f"[模板{template_id}-{index}] 請填入適當的詞語：課文中提到____是{subject}的重要概念。",
            "options": None,
            "answer": "知識",
            "explanation": f"從{subject}課文上下文脈絡可以推斷出應填入「知識」一詞。"
        },
        QuestionType.SHORT_ANSWER: {
            "prompt": f"[模板{template_id}-{index}] 請簡述{subject}課文的主要觀點。",
            "options": None,
            "answer": f"{subject}課文主要強調學習的重要性以及持續進步的價值。",
            "explanation": f"此答案涵蓋了{subject}課文的核心思想和主要論點。"
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
            chunk_id=2000 + template_id * 100 + index,
            chunk_text=f"來源文本塊 (文件{document_id}, 模板{template_id}): 這是與{subject}題目相關的課文內容..."
        )
    )
