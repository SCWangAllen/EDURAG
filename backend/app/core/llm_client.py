# app/core/llm_client.py
from typing import List, Dict, Any, Optional
import json
import logging
from app.core.config import USE_MOCK_API, ANTHROPIC_API_KEY
from app.schemas.question import QuestionType, Subject
from app.db.models import Template

# 設置日志記錄器
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

if not USE_MOCK_API:
    # 載入 Claude client
    from anthropic import AsyncAnthropic
    claude_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    
    def detect_question_type_from_template(template_content: str) -> List[QuestionType]:
        """從模板內容自動偵測題型"""
        content_lower = template_content.lower()
        detected_types = []
        
        # 檢測關鍵詞判斷題型
        if any(keyword in content_lower for keyword in ['選擇', 'choice', '選項', 'option', 'abcd', 'a.', 'b.', 'c.', 'd.']):
            detected_types.append(QuestionType.SINGLE_CHOICE)
            
        if any(keyword in content_lower for keyword in ['填空', 'cloze', '___', '____', '空格', 'blank']):
            detected_types.append(QuestionType.CLOZE)
            
        if any(keyword in content_lower for keyword in ['簡答', 'short answer', '說明', '解釋', '描述']):
            detected_types.append(QuestionType.SHORT_ANSWER)
            
        # 如果沒有檢測到特定類型，預設為混合型
        if not detected_types:
            detected_types = [QuestionType.SINGLE_CHOICE, QuestionType.CLOZE, QuestionType.SHORT_ANSWER]
            
        return detected_types

    async def generate_questions_by_template(
        context: str,
        template_content: str, 
        count: int
    ) -> List[Dict[str, Any]]:
        """基於模板生成題目"""
        logger.info(f"🚀 開始模板生成 - 請求生成 {count} 道題目")
        
        # 組合完整的 prompt
        full_prompt = f"""
{template_content.replace("{{context}}", context)}

請生成{count}道題目，並以 JSON 格式回傳，格式如下：

[
  {{
    "prompt": "題目內容",
    "options": ["A. 選項1", "B. 選項2", "C. 選項3", "D. 選項4"],  // 僅單選題需要，其他題型可省略
    "answer": "正確答案",
    "explanation": "詳細解釋"
  }}
]

請確保生成的是有效的 JSON 格式。
"""
        # logger.info(f"📝 完整 Prompt:full_prompt")
        logger.info(f"📝 完整 Prompt 長度: {len(full_prompt)} 字符")
        logger.info(f"📝 完整 Prompt 內容:\n{'-'*50}\n{full_prompt}\n{'-'*50}")
        
        logger.info("🤖 發送請求到 Claude API...")
        
        # 使用 Claude API 進行題目生成
        resp = await claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": full_prompt}]
        )
        response_content = resp.content[0].text
        
        logger.info(f"✅ Claude API 回應成功！")
        logger.info(f"📄 Claude 原始回應長度: {len(response_content)} 字符")
        logger.info(f"📄 Claude 原始回應內容:\n{'-'*50}\n{response_content}\n{'-'*50}")
        
        try:
            questions_data = json.loads(response_content)
            logger.info(f"✅ JSON 解析成功，解析出 {len(questions_data)} 道題目")
            
            # 記錄每道題目的詳細信息
            for i, q in enumerate(questions_data[:count]):
                logger.info(f"📝 題目 {i+1}:")
                logger.info(f"   - Prompt: {q.get('prompt', 'N/A')}")
                logger.info(f"   - Options: {q.get('options', 'N/A')}")
                logger.info(f"   - Answer: {q.get('answer', 'N/A')}")
                logger.info(f"   - Explanation: {q.get('explanation', 'N/A')[:100]}...")
            
            return questions_data[:count]
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON 解析失敗: {str(e)}")
            logger.error(f"❌ 無法解析的內容: {response_content[:500]}...")
            logger.info("🔄 使用 Fallback 題目")
            return _generate_fallback_questions(QuestionType.SINGLE_CHOICE, count)

    async def generate_questions_by_prompt(
        prompt: str,
        count: int,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        model: str = "claude-3-5-sonnet-20241022",
        question_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        logger.info(count)
        """直接基於前端提供的 prompt 生成題目"""
        logger.info(f"🚀 開始 Prompt 生成 - 請求生成 {count} 道題目")
        logger.info(f"📝 前端提供的 Prompt 長度: {len(prompt)} 字符")
        logger.info(f"🎯 指定問題類型: {question_type or '自動判斷'}")
        logger.info(f"📝 前端提供的 Prompt 內容:\n{'-'*50}\n{prompt}\n{'-'*50}")
        
        logger.info("🤖 發送請求到 Claude API (Prompt 模式)...")
        
        # 如果指定了問題類型，在 prompt 後面添加類型說明
        final_prompt = prompt
        if question_type:
            type_hints = {
                'single_choice': '請確保生成的是單選題，包含選項 A、B、C、D。',
                'cloze': '請確保生成的是填空題，在題目中用 ______ 標記填空位置。',
                'short_answer': '請確保生成的是簡答題，不需要選項。'
            }
            if question_type in type_hints:
                final_prompt += f"\n\n特別要求：{type_hints[question_type]}"
                logger.info(f"🎯 已添加類型提示: {type_hints[question_type]}")
        
        # 使用調整後的 prompt
        resp = await claude_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": final_prompt}]
        )
        response_content = resp.content[0].text
        
        logger.info(f"✅ Claude API 回應成功 (Prompt 模式)！")
        logger.info(f"📄 Claude 原始回應長度: {len(response_content)} 字符")
        logger.info(f"📄 Claude 原始回應內容:\n{'-'*50}\n{response_content}\n{'-'*50}")
        
        try:
            questions_data = json.loads(response_content)
            logger.info(f"✅ JSON 解析成功 (Prompt 模式)")
            logger.info(f"📊 解析的資料類型: {type(questions_data)}")
            
            # 確保 questions_data 是一個列表
            if not isinstance(questions_data, list):
                logger.error(f"❌ 預期是列表，但得到: {type(questions_data)}")
                logger.info("🔄 使用 Fallback 題目")
                return _generate_fallback_questions(QuestionType.SINGLE_CHOICE, count)
                
            logger.info(f"✅ 確認是列表，包含 {len(questions_data)} 道題目")
            
            # 記錄每道題目的詳細信息
            for i, q in enumerate(questions_data[:count]):
                logger.info(f"📝 題目 {i+1}:")
                logger.info(f"   - Prompt: {q.get('prompt', 'N/A')}")
                logger.info(f"   - Options: {q.get('options', 'N/A')}")
                logger.info(f"   - Answer: {q.get('answer', 'N/A')}")
                logger.info(f"   - Explanation: {q.get('explanation', 'N/A')[:100]}...")
            
            return questions_data[:count]
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON 解析失敗 (Prompt 模式): {str(e)}")
            logger.error(f"❌ 無法解析的內容: {response_content[:500]}...")
            logger.info("🔄 使用 Fallback 題目")
            return _generate_fallback_questions(QuestionType.SINGLE_CHOICE, count)

    async def generate_questions_by_type(
        context: str, 
        question_type: QuestionType, 
        count: int,
        subject: Optional[Subject] = None
    ) -> List[Dict[str, Any]]:
        """按題型生成指定數量的題目"""
        
        # 如果 subject 為 None，表示 context 已經是完整的 prompt（來自模板）
        if subject is None:
            # 直接使用完整的 prompt，只需添加 JSON 格式要求
            prompt = f"""
{context}

請生成{count}道題目，並以 JSON 格式回傳，格式如下：

[
  {{
    "prompt": "題目內容",
    "options": ["A. 選項1", "B. 選項2", "C. 選項3", "D. 選項4"],  // 僅單選題需要，其他題型可省略
    "answer": "正確答案",
    "explanation": "詳細解釋"
  }}
]

請確保生成的是有效的 JSON 格式。
"""
        else:
            # 傳統模式：使用 subject 和題型來建立 prompt
            type_prompts = {
                QuestionType.SINGLE_CHOICE: "單選題，需要提供4個選項（A、B、C、D）",
                QuestionType.CLOZE: "完形填空題，在適當位置留下空格",
                QuestionType.SHORT_ANSWER: "簡答題，需要簡短但完整的答案"
            }
            
            subject_names = {
                Subject.HEALTH: "健康",
                Subject.ENGLISH: "英文", 
                Subject.HISTORY: "歷史"
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
        
        logger.info(f"📝 傳統模式 Prompt 長度: {len(prompt)} 字符")
        logger.info(f"📝 傳統模式 Prompt 內容:\n{'-'*50}\n{prompt}\n{'-'*50}")
        
        logger.info("🤖 發送請求到 Claude API (傳統模式)...")
        
        # 使用 Claude API 進行題目生成
        resp = await claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        response_content = resp.content[0].text
        
        logger.info(f"✅ Claude API 回應成功 (傳統模式)！")
        logger.info(f"📄 Claude 原始回應長度: {len(response_content)} 字符")
        logger.info(f"📄 Claude 原始回應內容:\n{'-'*50}\n{response_content}\n{'-'*50}")
        
        try:
            questions_data = json.loads(response_content)
            logger.info(f"✅ JSON 解析成功 (傳統模式)，解析出 {len(questions_data)} 道題目")
            return questions_data[:count]  # 確保數量正確
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON 解析失敗 (傳統模式): {str(e)}")
            logger.error(f"❌ 無法解析的內容: {response_content[:500]}...")
            logger.info("🔄 使用 Fallback 題目 (傳統模式)")
            # 如果JSON解析失敗，回傳預設題目
            return _generate_fallback_questions(question_type, count)

else:
    # Mock 模式：回傳符合 schema 的假資料
    def detect_question_type_from_template(template_content: str) -> List[QuestionType]:
        """Mock 模式的題型偵測"""
        return [QuestionType.SINGLE_CHOICE, QuestionType.CLOZE, QuestionType.SHORT_ANSWER]
    
    async def generate_questions_by_template(
        context: str,
        template_content: str, 
        count: int
    ) -> List[Dict[str, Any]]:
        """Mock 模式：基於模板生成題目"""
        logger.info(f"🎭 Mock 模式：模板生成 {count} 道題目")
        return _generate_mock_questions(QuestionType.SINGLE_CHOICE, count)
    
    async def generate_questions_by_prompt(
        prompt: str,
        count: int,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        model: str = "claude-3-5-sonnet-20241022"
    ) -> List[Dict[str, Any]]:
        """Mock 模式：基於前端 prompt 生成題目"""
        logger.info(f"🎭 Mock 模式：Prompt 生成 {count} 道題目")
        logger.info(f"🎭 Mock 模式收到的 Prompt: {prompt[:200]}...")
        return _generate_mock_questions(QuestionType.SINGLE_CHOICE, count)
    
    async def generate_questions_by_type(
        context: str, 
        question_type: QuestionType, 
        count: int,
        subject: Optional[Subject] = None
    ) -> List[Dict[str, Any]]:
        logger.info(f"🎭 Mock 模式：傳統生成 {count} 道 {question_type} 題目")
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
