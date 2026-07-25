# app/core/llm_client.py
from typing import List, Dict, Any, Optional
import json
import re
import logging

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_not_exception_type,
)

from app.core.config import USE_MOCK_API, ANTHROPIC_API_KEY, LLM_MODEL_NAME
from app.schemas.question import QuestionType
from app.core.subject_norm import display_subject_zh
from app.core.question_types import build_format_instruction
from app.db.models import Template

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MODEL_NAME = LLM_MODEL_NAME
_LLM_BUFFER_COUNT = 2
# 許多模版的 max_tokens 偏小(500 / 1000),配上思考型模型(思考本身也吃 token)
# 會讓輸出 JSON 被截斷 → 解析失敗 → 0 題。給一個下限保證有足夠輸出空間;
# max_tokens 是上界不是目標,調高只是允許更長回應,不會讓短回應變長。
_MIN_MAX_TOKENS = 8192

if not USE_MOCK_API:
    from anthropic import (
        APIError,
        APITimeoutError,
        AsyncAnthropic,
        BadRequestError,
        RateLimitError,
    )

    claude_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    # ------------------------------------------------------------------ #
    #  Retry wrapper — 3 attempts, exponential backoff (2s → 4s → 8s)
    #  只重試「暫時性」錯誤;4xx(BadRequest/NotFound 等)是請求本身有問題,
    #  重試無用只是浪費時間 → 排除掉。
    # ------------------------------------------------------------------ #
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=8),
        retry=retry_if_exception_type((APIError, APITimeoutError, RateLimitError))
        & retry_if_not_exception_type(BadRequestError),
        before_sleep=lambda rs: logger.warning(
            f"Claude API call failed (attempt {rs.attempt_number}), retrying…"
        ),
        reraise=True,
    )
    async def _call_claude(
        prompt: str,
        *,
        model: str = MODEL_NAME,
        max_tokens: int = 16384,
        temperature: float = 0.7,
        top_p: Optional[float] = None,
    ) -> str:
        """Send a single prompt to Claude and return the text response."""
        api_params: Dict[str, Any] = {
            "model": model,
            "max_tokens": max(max_tokens, _MIN_MAX_TOKENS),
            "messages": [{"role": "user", "content": prompt}],
        }
        # 新版 Claude 模型(4.6+,含預設的 opus-4-8)拒絕同時指定 temperature
        # 與 top_p(會回 400)。所有模版 params 都同時帶這兩個,故只能擇一送出:
        # top_p=1.0 是無效果的預設 → 忽略,送 temperature;
        # 若老師明確設了非 1.0 的 top_p → 以 top_p 為準,略過 temperature。
        if top_p is not None and top_p != 1.0:
            api_params["top_p"] = top_p
        else:
            api_params["temperature"] = temperature

        logger.info("Sending request to Claude API…")
        logger.debug("Prompt length: %d chars", len(prompt))
        logger.debug("Prompt content:\n%s\n%s\n%s", "-" * 50, prompt, "-" * 50)

        try:
            resp = await claude_client.messages.create(**api_params)
        except BadRequestError as exc:
            # 自癒:新世代模型對 temperature/top_p 的規則各異(有的禁止並用、
            # 有的直接棄用 temperature)。若因這兩個取樣參數被拒,移除後用模型
            # 預設重試一次 —— model-agnostic,未來新增模型也不會壞。
            msg = str(exc).lower()
            hit = ("temperature" in msg or "top_p" in msg) and (
                "deprecat" in msg
                or "cannot both" in msg
                or "not supported" in msg
                or "unsupported" in msg
                or "invalid" in msg
            )
            if not hit or not (
                "temperature" in api_params or "top_p" in api_params
            ):
                raise
            api_params.pop("temperature", None)
            api_params.pop("top_p", None)
            logger.warning("模型不接受 temperature/top_p,移除後用預設重試")
            resp = await claude_client.messages.create(**api_params)
        # 最新模型(思考開啟)會把 ThinkingBlock 放在 content[0],硬取 [0].text 會爆。
        # 串接所有「文字塊」,略過 thinking 等非文字塊 —— model-agnostic。
        text = "".join(
            b.text for b in resp.content if getattr(b, "type", None) == "text"
        )
        if not text:
            logger.error(
                "回應無文字塊(content types=%s)",
                [getattr(b, "type", "?") for b in resp.content],
            )

        logger.info("Claude API responded (%d chars)", len(text))
        logger.debug("Response content:\n%s\n%s\n%s", "-" * 50, text, "-" * 50)
        return text

    # ------------------------------------------------------------------ #
    #  JSON extraction helpers
    # ------------------------------------------------------------------ #
    def _collect_json_objects(text: str) -> List[Dict[str, Any]]:
        """依序抓出文字中所有頂層 JSON 物件。

        處理「未包成陣列、以換行/空白分隔的多個 {…}」(JSONL 風格)——
        某些模型(如 opus-4-8)常這樣輸出,直接 json.loads 會在第二個物件
        報 Extra data。用 raw_decode 逐一解析,遇壞物件跳到下一個 {,穩健且
        model-agnostic。也能吃「前後夾雜散文」的單一物件。
        """
        decoder = json.JSONDecoder()
        objs: List[Dict[str, Any]] = []
        idx = text.find("{")
        while idx != -1:
            try:
                obj, end = decoder.raw_decode(text, idx)
            except json.JSONDecodeError:
                idx = text.find("{", idx + 1)
                continue
            if isinstance(obj, dict):
                objs.append(obj)
            idx = text.find("{", max(end, idx + 1))
        return objs

    def _extract_json_from_response(response: str) -> Optional[str]:
        """Extract JSON payload from an LLM response that may contain markdown."""
        # Method 1: ```json … ``` code block
        code_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response, re.IGNORECASE)
        if code_match:
            return code_match.group(1).strip()

        # Method 2: balanced bracket matching for [ … ]
        start = response.find("[")
        if start != -1:
            depth = 0
            for i in range(start, len(response)):
                if response[i] == "[":
                    depth += 1
                elif response[i] == "]":
                    depth -= 1
                    if depth == 0:
                        return response[start : i + 1]

        # Method 3: collect individual { … } objects
        objects = re.findall(r"\{[\s\S]*?\}", response)
        if objects:
            return "[" + ",".join(objects) + "]"

        logger.warning("Could not extract JSON from response")
        return None

    def _parse_questions_json(raw: str, count: int, fallback_type: QuestionType) -> List[Dict[str, Any]]:
        """Parse raw LLM text into a list of question dicts with fallback."""
        data = None
        # Attempt 1: 直接 parse(正規陣列 / 單一物件 / {"questions":[…]})
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Attempt 2: 連續/換行分隔的多個 JSON 物件(opus 等常見)
            objs = _collect_json_objects(raw)
            if objs:
                logger.debug("以連續物件模式解析出 %d 個物件", len(objs))
                data = objs
            else:
                # Attempt 3: markdown code block / 括號擷取(舊路徑)
                logger.debug("Direct JSON parse failed, attempting extraction…")
                extracted = _extract_json_from_response(raw)
                if not extracted:
                    logger.error("JSON extraction returned nothing")
                    return []
                try:
                    data = json.loads(extracted)
                except json.JSONDecodeError as exc:
                    logger.error("JSON parse failed after extraction: %s", exc)
                    return []

        # Handle {"questions": [...]} wrapper format (backward compatibility)
        if isinstance(data, dict) and "questions" in data:
            logger.debug("Unwrapping 'questions' field from response object")
            data = data["questions"]

        # 單一題目物件 → 包成 list
        if isinstance(data, dict):
            data = [data]

        if not isinstance(data, list):
            logger.error("Expected list, got %s", type(data).__name__)
            return []

        # 穩健:模型偶爾在陣列裡混入非物件元素(裸字串等),過濾掉,
        # 否則下游對 str 呼叫 .get() 會整個 500。
        bad = [d for d in data if not isinstance(d, dict)]
        if bad:
            logger.warning("忽略 %d 個非物件元素(如裸字串)", len(bad))
            data = [d for d in data if isinstance(d, dict)]

        logger.info("Parsed %d questions from response", len(data))
        for i, q in enumerate(data[:count]):
            logger.debug(
                "Question %d: prompt=%s, answer=%s",
                i + 1,
                q.get("prompt", "N/A")[:80],
                str(q.get("answer", "N/A"))[:80],
            )
        return data[:count]

    # ------------------------------------------------------------------ #
    #  Question-type detection
    # ------------------------------------------------------------------ #
    def detect_question_type_from_template(template_content: str) -> List[QuestionType]:
        """Detect question types from template content keywords."""
        lower = template_content.lower()
        detected: List[QuestionType] = []

        keyword_map = {
            QuestionType.SINGLE_CHOICE: ["選擇", "choice", "選項", "option", "abcd", "a.", "b.", "c.", "d."],
            QuestionType.CLOZE: ["填空", "cloze", "___", "____", "空格", "blank"],
            QuestionType.SHORT_ANSWER: ["簡答", "short answer", "說明", "解釋", "描述"],
            QuestionType.TRUE_FALSE: ["是非", "true false", "對錯", "正確錯誤", "true/false"],
            QuestionType.MATCHING: ["配對", "matching", "連連看", "配連", "對應"],
        }

        for qtype, keywords in keyword_map.items():
            if any(kw in lower for kw in keywords):
                detected.append(qtype)

        if not detected:
            detected = [QuestionType.SINGLE_CHOICE, QuestionType.CLOZE, QuestionType.SHORT_ANSWER]

        return detected

    # ------------------------------------------------------------------ #
    #  Question format validation
    # ------------------------------------------------------------------ #
    def validate_question_format(questions: List[Dict[str, Any]], question_type: str) -> List[Dict[str, Any]]:
        """Validate generated questions match the expected format for the given type."""
        validated = []

        for q in questions:
            if not q.get("prompt") or not q.get("answer") or not q.get("explanation"):
                logger.warning("Question missing required fields: %s", list(q.keys()))
                continue

            if question_type == "true_false":
                if str(q.get("answer", "")).lower() not in ("true", "false"):
                    logger.warning("True/false answer format invalid: %s", q.get("answer"))
                    continue

            elif question_type == "matching":
                qd = q.get("question_data")
                # 容錯：如果 question_data 不存在，嘗試從頂層字段構建
                if not qd:
                    left_top = q.get("left_items")
                    right_top = q.get("right_items")
                    if isinstance(left_top, list) and isinstance(right_top, list) and left_top and right_top:
                        qd = {"left_items": left_top, "right_items": right_top}
                        q["question_data"] = qd
                        logger.info("Matching: auto-constructed question_data from top-level fields")
                    else:
                        logger.warning("Matching question missing question_data and no fallback fields found: %s", list(q.keys()))
                        continue
                left = qd.get("left_items")
                right = qd.get("right_items")
                if not isinstance(left, list) or not isinstance(right, list) or not left or not right:
                    logger.warning("Matching question_data format invalid: left=%s, right=%s", type(left), type(right))
                    continue

            elif question_type == "single_choice":
                opts = q.get("options")
                if not isinstance(opts, list) or len(opts) < 2:
                    logger.warning("Single-choice options invalid")
                    continue

            elif question_type == "sequence":
                items = q.get("items")
                answer = q.get("answer")
                if not isinstance(items, list) or not items:
                    logger.warning("Sequence question missing or invalid 'items' array")
                    continue
                if not isinstance(answer, list) or not answer:
                    logger.warning("Sequence question missing or invalid 'answer' array")
                    continue
                # 標準化:把待排序項收進 question_data,讓下游 assembly 能存進
                # questions.question_data JSONB(否則排序資料會遺失)。
                qd = q.get("question_data")
                if not isinstance(qd, dict):
                    qd = {}
                qd.setdefault("items", items)
                q["question_data"] = qd

            elif question_type == "enumeration":
                answer = q.get("answer")
                if not isinstance(answer, list) or not answer:
                    logger.warning("Enumeration question missing or invalid 'answer' array")
                    continue

            elif question_type == "symbol_identification":
                symbols = q.get("symbols")
                if not isinstance(symbols, list) or not symbols:
                    logger.warning("Symbol identification question missing or invalid 'symbols' array")
                    continue

            validated.append(q)

        logger.info("Validation: %d/%d questions passed", len(validated), len(questions))
        return validated

    # ------------------------------------------------------------------ #
    #  Type hints for prompt-mode generation
    # ------------------------------------------------------------------ #
    _TYPE_HINTS: Dict[str, str] = {
        "single_choice": (
            "Ensure generated questions are multiple choice with exactly 4 options (A, B, C, D). "
            'Include "options" array in response.'
        ),
        "cloze": (
            "Ensure generated questions are fill-in-the-blank with ______ marking blank spaces. "
            'No "options" field needed.'
        ),
        "short_answer": (
            "Ensure generated questions require short written answers (1-3 sentences). "
            'No "options" field needed.'
        ),
        "true_false": (
            "Ensure generated questions are true/false statements. "
            'The "answer" field MUST be exactly "true" or "false" (lowercase). '
            'No "options" field needed.'
        ),
        "matching": (
            "CRITICAL: Generate matching questions with this EXACT structure:\n"
            '- MUST include "question_data" object containing:\n'
            '  - "left_items": array of 3-5 terms/concepts\n'
            '  - "right_items": array of 3-5 matching definitions/descriptions\n'
            '- "answer" field describes correct pairings as "Term-Definition" pairs\n'
            '- No "options" field needed\n\n'
            'Required JSON structure:\n'
            '{"prompt": "Match instruction", '
            '"question_data": {"left_items": ["A", "B", "C"], "right_items": ["1", "2", "3"]}, '
            '"answer": "A-2, B-3, C-1", "explanation": "..."}'
        ),
        "sequence": (
            "Ensure generated questions require ordering items in sequence:\n"
            '- Include "items" field with array of items in scrambled order\n'
            '- "answer" field contains array of items in correct order\n'
            '- No "options" field needed'
        ),
        "enumeration": (
            "Ensure generated questions ask students to list items:\n"
            '- "prompt" should specify how many items to list\n'
            '- "answer" field contains array of correct items\n'
            '- No "options" field needed'
        ),
        "symbol_identification": (
            "Ensure generated questions test symbol recognition:\n"
            '- Include "symbols" field with array of symbol options\n'
            '- "answer" field contains correct symbol meaning/name\n'
            '- No "options" field needed'
        ),
        "mixed": (
            "Generate a variety of question types. Each question should include "
            'a "type" field indicating its question type.'
        ),
        "auto": (
            "Automatically determine the most appropriate question type based on the content. "
            "Use the format that best tests the concepts."
        ),
    }

    # ------------------------------------------------------------------ #
    #  Shared JSON-format suffix
    # ------------------------------------------------------------------ #
    _JSON_FORMAT_SUFFIX = """
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

    # ------------------------------------------------------------------ #
    #  Public generation functions
    # ------------------------------------------------------------------ #
    async def generate_questions_by_template(
        context: str,
        template_content: str,
        count: int,
        model: str = MODEL_NAME,
    ) -> List[Dict[str, Any]]:
        """Generate questions based on a template."""
        logger.info("Template generation — requesting %d questions", count)

        full_prompt = (
            template_content.replace("{context}", context)
            + _JSON_FORMAT_SUFFIX.format(count=count)
        )

        raw = await _call_claude(full_prompt, model=model)
        return _parse_questions_json(raw, count, QuestionType.SINGLE_CHOICE)

    async def generate_questions_by_prompt(
        prompt: str,
        count: int,
        temperature: float = 0.7,
        max_tokens: int = 16384,
        model: str = MODEL_NAME,
        question_type: Optional[str] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Generate questions from a free-form prompt with optional type hints."""
        detected_type = question_type or "single_choice"
        buffer_count = count + _LLM_BUFFER_COUNT
        logger.info(
            "Prompt generation — requesting %d questions (type=%s, buffer=%d)",
            count, detected_type, buffer_count,
        )

        final_prompt = prompt
        # 依 question_type 由後端注入權威的輸出 JSON 格式(單一真實來源),
        # 老師的模版只需寫指示語。未收錄的題型 fallback 到既有 _TYPE_HINTS。
        format_instruction = build_format_instruction(detected_type)
        if format_instruction:
            final_prompt += f"\n\n{format_instruction}"
        elif detected_type in _TYPE_HINTS:
            final_prompt += f"\n\n格式要求：{_TYPE_HINTS[detected_type]}"
        final_prompt += f"\n\nIMPORTANT: Please generate exactly {buffer_count} questions in total."

        raw = await _call_claude(
            final_prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )

        questions = _parse_questions_json(raw, buffer_count, QuestionType.SINGLE_CHOICE)

        validated = validate_question_format(questions, detected_type)
        if not validated:
            logger.warning("All questions failed validation, returning empty list")
            return []

        if len(validated) < count:
            logger.warning("Only %d/%d questions passed validation", len(validated), count)

        return validated[:count]

    async def generate_questions_by_type(
        context: str,
        question_type: QuestionType,
        count: int,
        subject: Optional[str] = None,
        model: str = MODEL_NAME,
    ) -> List[Dict[str, Any]]:
        """Generate questions by type — traditional mode or template-passthrough."""
        if subject is None:
            full_prompt = context + _JSON_FORMAT_SUFFIX.format(count=count)
        else:
            type_prompts = {
                QuestionType.SINGLE_CHOICE: "單選題，需要提供4個選項（A、B、C、D）",
                QuestionType.CLOZE: "完形填空題，在適當位置留下空格",
                QuestionType.SHORT_ANSWER: "簡答題，需要簡短但完整的答案",
                QuestionType.TRUE_FALSE: "是非題，學生需判斷陳述正確或錯誤",
                QuestionType.MATCHING: "配對題，提供左右兩列項目供學生配對，需包含question_data欄位",
            }
            full_prompt = f"""
你是一位專業的{display_subject_zh(subject)}老師。基於以下教材內容，製作{count}道{type_prompts[question_type]}。

教材內容：
{context}

要求：
1. 題目必須基於提供的教材內容
2. 生成{count}道{question_type.value}題目
3. 每題都要包含詳細解釋
4. 請以 JSON 格式回傳，格式如下：

[
  {{{{
    "prompt": "題目內容",
    "options": ["A. 選項1", "B. 選項2", "C. 選項3", "D. 選項4"],  // 僅單選題需要
    "answer": "正確答案",
    "explanation": "詳細解釋"
  }}}}
]

請確保生成的是有效的 JSON 格式。
"""

        logger.info("Type generation (%s) — requesting %d questions", question_type.value, count)
        raw = await _call_claude(full_prompt, model=model)
        return _parse_questions_json(raw, count, question_type)
