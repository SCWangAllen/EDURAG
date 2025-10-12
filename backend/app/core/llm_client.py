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
            
        # G1~G2 新增題型檢測
        if any(keyword in content_lower for keyword in ['是非', 'true false', '對錯', '正確錯誤', 'true/false']):
            detected_types.append(QuestionType.TRUE_FALSE)
            
        if any(keyword in content_lower for keyword in ['配對', 'matching', '連連看', '配連', '對應']):
            detected_types.append(QuestionType.MATCHING)
            
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
            logger.info("🔍 直接JSON解析失敗，嘗試提取JSON部分...")
            json_content = _extract_json_from_response(response_content)
            if json_content:
                try:
                    questions_data = json.loads(json_content)
                    logger.info(f"✅ JSON 提取並解析成功，解析出 {len(questions_data)} 道題目")
                    
                    # 記錄每道題目的詳細信息
                    for i, q in enumerate(questions_data[:count]):
                        logger.info(f"📝 題目 {i+1}:")
                        logger.info(f"   - Prompt: {q.get('prompt', 'N/A')}")
                        logger.info(f"   - Options: {q.get('options', 'N/A')}")
                        logger.info(f"   - Answer: {q.get('answer', 'N/A')}")
                        logger.info(f"   - Explanation: {q.get('explanation', 'N/A')[:100]}...")
                    
                    return questions_data[:count]
                except json.JSONDecodeError as e2:
                    logger.error(f"❌ JSON 解析失敗: {str(e2)}")
                    logger.error(f"❌ 無法解析的內容: {json_content[:500]}...")
                    logger.info("🔄 使用 Fallback 題目")
                    return _generate_fallback_questions(QuestionType.SINGLE_CHOICE, count)
            else:
                logger.error(f"❌ JSON 解析失敗: {str(e)}")
                logger.error(f"❌ 無法解析的內容: {response_content[:500]}...")
                logger.info("🔄 使用 Fallback 題目")
                return _generate_fallback_questions(QuestionType.SINGLE_CHOICE, count)

    def validate_question_format(questions: List[Dict[str, Any]], question_type: str) -> List[Dict[str, Any]]:
        """驗證題目格式是否符合指定題型要求"""
        validated_questions = []
        
        for q in questions:
            is_valid = True
            
            # 基本欄位檢查
            if not q.get('prompt') or not q.get('answer') or not q.get('explanation'):
                logger.warning(f"⚠️  題目缺少基本欄位: {q}")
                is_valid = False
                continue
            
            # 根據題型進行特定驗證
            if question_type == 'true_false':
                answer = str(q.get('answer', '')).lower()
                if answer not in ['true', 'false']:
                    logger.warning(f"⚠️  是非題答案格式錯誤: {q.get('answer')}")
                    is_valid = False
                    
            elif question_type == 'matching':
                question_data = q.get('question_data')
                if not question_data:
                    logger.warning(f"⚠️  配對題缺少 question_data 欄位")
                    is_valid = False
                else:
                    left_items = question_data.get('left_items')
                    right_items = question_data.get('right_items')
                    if not left_items or not right_items or not isinstance(left_items, list) or not isinstance(right_items, list):
                        logger.warning(f"⚠️  配對題 question_data 格式錯誤")
                        is_valid = False
                    elif len(left_items) != len(right_items):
                        logger.warning(f"⚠️  配對題左右項目數量不一致: {len(left_items)} vs {len(right_items)}")
                        # 允許數量不同但記錄警告
                        
            elif question_type == 'single_choice':
                options = q.get('options')
                if not options or not isinstance(options, list) or len(options) < 2:
                    logger.warning(f"⚠️  單選題選項格式錯誤")
                    is_valid = False
                    
            # 如果驗證通過，加入結果
            if is_valid:
                validated_questions.append(q)
            
        logger.info(f"📊 格式驗證結果: {len(validated_questions)}/{len(questions)} 道題目通過驗證")
        return validated_questions


    async def generate_questions_by_prompt(
        prompt: str,
        count: int,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        model: str = "claude-3-5-sonnet-20241022",
        question_type: Optional[str] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """直接基於前端提供的 prompt 和指定題型生成題目"""
        logger.info(f"🚀 開始 Prompt 生成 - 請求生成 {count} 道題目")
        logger.info(f"📝 前端提供的 Prompt 長度: {len(prompt)} 字符")
        logger.info(f"📝 前端提供的 Prompt 內容:\n{'-'*50}\n{prompt}\n{'-'*50}")

        # 使用傳入的 question_type 參數，預設為 single_choice
        detected_type = question_type or 'single_choice'
        logger.info(f"🎯 使用的問題類型: {detected_type}")

        # 多生成 2 題作為緩衝，避免驗證後數量不足
        buffer_count = count + 2
        logger.info(f"💡 實際向 LLM 請求 {buffer_count} 題（含 2 題緩衝）")
        
        logger.info("🤖 發送請求到 Claude API (Prompt 模式)...")
        
        # 擴展的 type_hints（支援所有10種題型，英文版）
        type_hints = {
            # 基本題型
            'single_choice': 'Ensure generated questions are multiple choice with exactly 4 options (A, B, C, D). Include "options" array in response.',

            'cloze': 'Ensure generated questions are fill-in-the-blank with ______ marking blank spaces. No "options" field needed.',

            'short_answer': 'Ensure generated questions require short written answers (1-3 sentences). No "options" field needed.',

            # 是非與配對題型
            'true_false': 'Ensure generated questions are true/false statements. The "answer" field MUST be exactly "true" or "false" (lowercase). No "options" field needed.',

            'matching': '''Ensure generated questions are matching format with these requirements:
- Include "question_data" field with "left_items" and "right_items" arrays
- "answer" field describes correct pairings
- No "options" field needed
Example: {"question_data": {"left_items": ["Item 1", "Item 2"], "right_items": ["Match A", "Match B"]}, "answer": "Item 1-Match A, Item 2-Match B"}''',

            # 進階題型
            'sequence': '''Ensure generated questions require ordering items in sequence:
- Include "items" field with array of items in scrambled order
- "answer" field contains array of items in correct order
- No "options" field needed
Example: {"items": ["Step 3", "Step 1", "Step 2"], "answer": ["Step 1", "Step 2", "Step 3"]}''',

            'enumeration': '''Ensure generated questions ask students to list items:
- "prompt" should specify how many items to list
- "answer" field contains array of correct items
- No "options" field needed
Example: {"prompt": "List three...", "answer": ["Item 1", "Item 2", "Item 3"]}''',

            'symbol_identification': '''Ensure generated questions test symbol recognition:
- Include "symbols" field with array of symbol options
- "answer" field contains correct symbol meaning/name
- No "options" field needed
Example: {"symbols": ["Symbol A", "Symbol B"], "answer": "Correct meaning"}''',

            # 特殊題型
            'mixed': 'Generate a variety of question types. Each question should include a "type" field indicating its question type.',

            'auto': 'Automatically determine the most appropriate question type based on the content. Use the format that best tests the concepts.'
        }
        
        # 基於檢測到的題型添加格式要求
        final_prompt = prompt
        if detected_type in type_hints:
            final_prompt += f"\n\n格式要求：{type_hints[detected_type]}"
            logger.info(f"🎯 已添加 {detected_type} 類型的格式要求")

        # 在 Prompt 中加入實際請求數量（使用緩衝數量）
        final_prompt += f"\n\nIMPORTANT: Please generate exactly {buffer_count} questions in total."
        logger.info(f"📝 已在 Prompt 中要求生成 {buffer_count} 題")
        
        # 構建 API 參數
        api_params = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": final_prompt}]
        }
        
        # 添加可選參數
        if top_p is not None:
            api_params["top_p"] = top_p
        if frequency_penalty is not None:
            # 注意：Claude API 使用的是不同的參數名
            logger.info(f"🎛️ 設定 frequency_penalty: {frequency_penalty}")
        
        # 使用調整後的 prompt
        resp = await claude_client.messages.create(**api_params)
        response_content = resp.content[0].text
        
        logger.info(f"✅ Claude API 回應成功 (Prompt 模式)！")
        logger.info(f"📄 Claude 原始回應長度: {len(response_content)} 字符")
        logger.info(f"📄 Claude 原始回應內容:\n{'-'*50}\n{response_content}\n{'-'*50}")
        
        try:
            # 先嘗試直接解析
            questions_data = json.loads(response_content)
            logger.info(f"✅ JSON 解析成功 (Prompt 模式)")
            logger.info(f"📊 解析的資料類型: {type(questions_data)}")
        except json.JSONDecodeError:
            # 如果直接解析失敗，嘗試提取JSON部分
            logger.info("🔍 直接JSON解析失敗，嘗試提取JSON部分...")
            json_content = _extract_json_from_response(response_content)
            if json_content:
                try:
                    questions_data = json.loads(json_content)
                    logger.info(f"✅ JSON 提取並解析成功 (Prompt 模式)")
                    logger.info(f"📊 解析的資料類型: {type(questions_data)}")
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON 解析失敗 (Prompt 模式): {str(e)}")
                    logger.error(f"❌ 無法解析的內容: {json_content[:500]}...")
                    logger.info("🔄 使用 Fallback 題目")
                    return _generate_fallback_questions(QuestionType.SINGLE_CHOICE, count)
            else:
                logger.error(f"❌ 無法從回應中提取JSON")
                logger.error(f"❌ 無法解析的內容: {response_content[:500]}...")
                logger.info("🔄 使用 Fallback 題目")
                return _generate_fallback_questions(QuestionType.SINGLE_CHOICE, count)
                
        try:
            
            # 確保 questions_data 是一個列表
            if not isinstance(questions_data, list):
                logger.error(f"❌ 預期是列表，但得到: {type(questions_data)}")
                logger.info("🔄 使用 Fallback 題目")
                return _generate_fallback_questions(QuestionType.SINGLE_CHOICE, count)
                
            logger.info(f"✅ 確認是列表，包含 {len(questions_data)} 道題目")

            # 驗證題型格式是否正確（驗證所有生成的題目，不預先切片）
            validated_questions = validate_question_format(questions_data, detected_type)
            logger.info(f"📊 格式驗證完成: {len(validated_questions)}/{len(questions_data)} 題通過驗證")

            if not validated_questions:
                logger.warning(f"⚠️  所有題目格式驗證失敗，使用 Fallback")
                return _generate_fallback_questions(getattr(QuestionType, detected_type.upper(), QuestionType.SINGLE_CHOICE), count)

            # 檢查驗證後數量是否足夠
            if len(validated_questions) < count:
                logger.warning(f"⚠️  驗證後題目數量不足: {len(validated_questions)}/{count}")
                logger.warning(f"⚠️  將返回所有通過驗證的 {len(validated_questions)} 題")

            # 取前 count 題返回（如果有足夠的話）
            final_questions = validated_questions[:count]

            # 記錄每道題目的詳細信息
            for i, q in enumerate(final_questions):
                logger.info(f"📝 最終題目 {i+1}/{len(final_questions)}:")
                logger.info(f"   - Prompt: {q.get('prompt', 'N/A')}")
                logger.info(f"   - Options: {q.get('options', 'N/A')}")
                logger.info(f"   - Answer: {q.get('answer', 'N/A')}")
                logger.info(f"   - Explanation: {q.get('explanation', 'N/A')[:100]}...")
                if q.get('question_data'):
                    logger.info(f"   - Question_data: {q.get('question_data')}")

            logger.info(f"✅ 成功返回 {len(final_questions)} 道題目（需求: {count} 題）")
            return final_questions
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
                QuestionType.SHORT_ANSWER: "簡答題，需要簡短但完整的答案",
                # G1~G2 新增題型  
                QuestionType.TRUE_FALSE: "是非題，學生需判斷陳述正確或錯誤",
                QuestionType.MATCHING: "配對題，提供左右兩列項目供學生配對，需包含question_data欄位"
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
            logger.info("🔍 直接JSON解析失敗，嘗試提取JSON部分...")
            json_content = _extract_json_from_response(response_content)
            if json_content:
                try:
                    questions_data = json.loads(json_content)
                    logger.info(f"✅ JSON 提取並解析成功 (傳統模式)，解析出 {len(questions_data)} 道題目")
                    return questions_data[:count]
                except json.JSONDecodeError as e2:
                    logger.error(f"❌ JSON 解析失敗 (傳統模式): {str(e2)}")
                    logger.error(f"❌ 無法解析的內容: {json_content[:500]}...")
                    logger.info("🔄 使用 Fallback 題目 (傳統模式)")
                    return _generate_fallback_questions(question_type, count)
            else:
                logger.error(f"❌ JSON 解析失敗 (傳統模式): {str(e)}")
                logger.error(f"❌ 無法解析的內容: {response_content[:500]}...")
                logger.info("🔄 使用 Fallback 題目 (傳統模式)")
                return _generate_fallback_questions(question_type, count)

def _extract_json_from_response(response: str) -> str:
    """從LLM回應中提取JSON部分"""
    import re
    
    # 方法1: 尋找 [ ] 包圍的JSON陣列
    array_pattern = r'\[[\s\S]*?\]'
    array_match = re.search(array_pattern, response)
    if array_match:
        json_content = array_match.group(0)
        logger.info(f"🔍 找到JSON陣列，長度: {len(json_content)}")
        return json_content
    
    # 方法2: 尋找 { } 包圍的JSON物件（多個）
    object_pattern = r'\{[\s\S]*?\}'
    object_matches = re.findall(object_pattern, response)
    if object_matches:
        # 將多個JSON物件包裝成陣列
        json_content = '[' + ','.join(object_matches) + ']'
        logger.info(f"🔍 找到 {len(object_matches)} 個JSON物件，組合成陣列")
        return json_content
    
    # 方法3: 尋找```json...```代碼塊
    code_block_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    code_match = re.search(code_block_pattern, response, re.IGNORECASE)
    if code_match:
        json_content = code_match.group(1).strip()
        logger.info(f"🔍 找到代碼塊中的JSON，長度: {len(json_content)}")
        return json_content
    
    logger.warning("⚠️ 無法從回應中提取JSON")
    return None

def _generate_fallback_questions(question_type: QuestionType, count: int) -> List[Dict[str, Any]]:
    """LLM失敗時的備用題目生成"""
    logger.error(f"❌ LLM生成失敗，無法提供備用題目")
    return []
