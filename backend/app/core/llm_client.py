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
)

from app.core.config import USE_MOCK_API, ANTHROPIC_API_KEY, LLM_MODEL_NAME
from app.schemas.question import QuestionType, Subject
from app.db.models import Template

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MODEL_NAME = LLM_MODEL_NAME
_LLM_BUFFER_COUNT = 2

if not USE_MOCK_API:
    from anthropic import AsyncAnthropic, APIError, APITimeoutError, RateLimitError

    claude_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    # ------------------------------------------------------------------ #
    #  Retry wrapper — 3 attempts, exponential backoff (2s → 4s → 8s)
    # ------------------------------------------------------------------ #
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=8),
        retry=retry_if_exception_type((APIError, APITimeoutError, RateLimitError)),
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
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if top_p is not None:
            api_params["top_p"] = top_p

        logger.info("Sending request to Claude API…")
        logger.debug("Prompt length: %d chars", len(prompt))
        logger.debug("Prompt content:\n%s\n%s\n%s", "-" * 50, prompt, "-" * 50)

        resp = await claude_client.messages.create(**api_params)
        text = resp.content[0].text

        logger.info("Claude API responded (%d chars)", len(text))
        logger.debug("Response content:\n%s\n%s\n%s", "-" * 50, text, "-" * 50)
        return text

    # ------------------------------------------------------------------ #
    #  JSON extraction helpers
    # ------------------------------------------------------------------ #
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
        # Attempt 1: direct parse
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
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

        if not isinstance(data, list):
            logger.error("Expected list, got %s", type(data).__name__)
            return []

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
    ) -> List[Dict[str, Any]]:
        """Generate questions based on a template."""
        logger.info("Template generation — requesting %d questions", count)

        full_prompt = (
            template_content.replace("{{context}}", context)
            + _JSON_FORMAT_SUFFIX.format(count=count)
        )

        raw = await _call_claude(full_prompt)
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
        if detected_type in _TYPE_HINTS:
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
        subject: Optional[Subject] = None,
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
            subject_names = {
                Subject.HEALTH: "健康",
                Subject.ENGLISH: "英文",
                Subject.HISTORY: "歷史",
            }
            full_prompt = f"""
你是一位專業的{subject_names[subject]}老師。基於以下教材內容，製作{count}道{type_prompts[question_type]}。

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
        raw = await _call_claude(full_prompt)
        return _parse_questions_json(raw, count, question_type)
