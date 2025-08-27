# app/core/llm_client.py
from typing import List, Dict, Any
import json
from app.core.config import USE_MOCK_API, OPENAI_API_KEY
from app.schemas.question import QuestionType, Subject

if not USE_MOCK_API:
    # 真實模式：載入 OpenAI client 並呼叫 Chat Completions API
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    async def generate_questions_by_type(
        context: str, 
        question_type: QuestionType, 
        count: int,
        subject: Subject
    ) -> List[Dict[str, Any]]:
        """按題型生成指定數量的題目"""
        
        # 根據題型建立不同的提示詞
        type_prompts = {
            QuestionType.SINGLE_CHOICE: "單選題，需要提供4個選項（A、B、C、D）",
            QuestionType.CLOZE: "完形填空題，在適當位置留下空格",
            QuestionType.SHORT_ANSWER: "簡答題，需要簡短但完整的答案"
        }
        
        subject_names = {
            Subject.CHINESE: "國文",
            Subject.ENGLISH: "英文", 
            Subject.MATH: "數學"
        }
        
        prompt = f"""
你是一位專業的{subject_names[subject]}老師。基於以下教材內容，製作{count}道{type_prompts[question_type]}。

教材內容：
{context}

要求：
1. 題目必須基於提供的教材內容
2. 生成{count}道{question_type.value}題目
3. 每題都要包含詳細解釋
4. 請以 JSON 格式回傳，格式如下：

[
  {{
    "prompt": "題目內容",
    "options": ["A. 選項1", "B. 選項2", "C. 選項3", "D. 選項4"],  // 僅單選題需要
    "answer": "正確答案",
    "explanation": "詳細解釋"
  }}
]

請確保生成的是有效的 JSON 格式。
        """
        
        resp = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500
        )
        
        try:
            questions_data = json.loads(resp.choices[0].message.content)
            return questions_data[:count]  # 確保數量正確
        except json.JSONDecodeError:
            # 如果JSON解析失敗，回傳預設題目
            return _generate_fallback_questions(question_type, count)

else:
    # Mock 模式：回傳符合 schema 的假資料
    async def generate_questions_by_type(
        context: str, 
        question_type: QuestionType, 
        count: int,
        subject: Subject
    ) -> List[Dict[str, Any]]:
        return _generate_mock_questions(question_type, count)

def _generate_mock_questions(question_type: QuestionType, count: int) -> List[Dict[str, Any]]:
    """生成Mock題目資料"""
    mock_data = {
        QuestionType.SINGLE_CHOICE: {
            "prompt": "根據課文內容，下列何者正確？",
            "options": ["A. 選項一", "B. 選項二", "C. 正確選項", "D. 選項四"],
            "answer": "C",
            "explanation": "根據課文第三段內容可知，選項C是正確答案。"
        },
        QuestionType.CLOZE: {
            "prompt": "請填入適當的詞語：文章中提到____是重要概念。",
            "options": None,
            "answer": "知識",
            "explanation": "從上下文脈絡可以推斷出應填入「知識」一詞。"
        },
        QuestionType.SHORT_ANSWER: {
            "prompt": "請簡述課文的主要觀點。",
            "options": None,
            "answer": "課文主要強調學習的重要性以及持續進步的價值。",
            "explanation": "此答案涵蓋了課文的核心思想和主要論點。"
        }
    }
    
    base_question = mock_data[question_type]
    questions = []
    
    for i in range(count):
        question = base_question.copy()
        question["prompt"] = f"[{i+1}] {question['prompt']}"
        questions.append(question)
    
    return questions

def _generate_fallback_questions(question_type: QuestionType, count: int) -> List[Dict[str, Any]]:
    """LLM失敗時的備用題目生成"""
    return _generate_mock_questions(question_type, count)
