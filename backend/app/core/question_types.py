"""題型單一真實來源(single source of truth)。

每個題型集中定義:顯示名、必填欄位、輸出 JSON 範例、起始模版(純指示語)。
用途:
  1. 生成時依 `question_type` 由後端**自動注入**輸出 JSON 格式(build_format_instruction),
     老師的模版只需寫「指示語」,不必手寫 JSON —— 避免寫錯 key 導致整批題目被丟、生成失敗。
  2. starter API(list_starters)給前端「題型範本庫」與 TemplateModal 選題型自動帶入。

起始範本以**英文**撰寫 —— 本產品題目一律出英文,而 AI 的輸出語言跟著範本(prompt)
的語言走,故 starter/example 皆用英文以產出英文題目。label 僅作 fallback,前端顯示
時改用 i18n 依 UI 語言呈現。

只收錄真正端到端支援的 7 種文字題型;key 與 schemas/question.py 的 QuestionType 一致。
（diagram_question 走圖片題另一條路;mixed/auto 為系統型,皆不在此。）

範例欄位需與 llm_client.validate_question_format 的各題型硬性規則一致:
  通則必填 prompt/answer/explanation;single_choice 需 options;matching 需
  question_data.{left_items,right_items};sequence 需 items(答案為陣列);
  enumeration 答案為陣列;true_false 答案為 "true"/"false"。
"""

import json
from typing import Any, Dict, List, Optional

QUESTION_TYPE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "single_choice": {
        "label": "Multiple Choice",
        "required": ["prompt", "options", "answer", "explanation"],
        "example": {
            "prompt": "The question stem",
            "options": ["A. First option", "B. Second option", "C. Third option", "D. Fourth option"],
            "answer": "B",
            "explanation": "Why this answer is correct",
        },
        "starter": (
            "Based on the following material, create multiple-choice questions for "
            "elementary students. Write everything in English.\n\n"
            "Material:\n{context}\n\n"
            "Requirements:\n"
            "1. Keep the question stem clear and age-appropriate\n"
            "2. Provide exactly 4 options (A, B, C, D) with only one correct answer\n"
            "3. Include a short explanation of the correct answer\n"
            "4. Stay within the material; do not go beyond it"
        ),
    },
    "cloze": {
        "label": "Fill in the Blank (Cloze)",
        "required": ["prompt", "answer", "explanation"],
        "example": {
            "prompt": "A sentence with ______ marking the blank to fill in",
            "answer": "the correct word",
            "explanation": "Why this word fits",
        },
        "starter": (
            "Based on the following material, create fill-in-the-blank (cloze) questions "
            "for elementary students. Write everything in English.\n\n"
            "Material:\n{context}\n\n"
            "Requirements:\n"
            "1. Use ______ to mark each blank\n"
            "2. Each blank tests one key concept, with enough context in the sentence\n"
            "3. Focus on important vocabulary and concepts; keep it age-appropriate"
        ),
    },
    "short_answer": {
        "label": "Short Answer",
        "required": ["prompt", "answer", "explanation"],
        "example": {
            "prompt": "A clear question asking for an explanation or description",
            "answer": "A model answer in 1-3 sentences",
            "explanation": "What key points a good answer should include",
        },
        "starter": (
            "Based on the following material, create short-answer questions for "
            "elementary students. Write everything in English.\n\n"
            "Material:\n{context}\n\n"
            "Requirements:\n"
            "1. Ask clear, direct questions\n"
            "2. Model answers should be about 1-3 sentences\n"
            "3. Test understanding rather than memorization; keep it age-appropriate\n"
            "4. Note the key points for grading"
        ),
    },
    "true_false": {
        "label": "True/False",
        "required": ["prompt", "answer", "explanation"],
        "example": {
            "prompt": "A clear statement that is either true or false",
            "answer": "true",
            "explanation": "Why the statement is true or false",
        },
        "starter": (
            "Based on the following material, create true/false questions for "
            "elementary students. Write everything in English.\n\n"
            "Material:\n{context}\n\n"
            "Requirements:\n"
            "1. Make clear, definitive statements; avoid ambiguity or trick questions\n"
            "2. Test important concepts, not trivial details\n"
            "3. Include the reason the statement is true or false\n"
            'Note: the answer must be exactly "true" or "false" (lowercase).'
        ),
    },
    "matching": {
        "label": "Matching",
        "required": ["prompt", "question_data", "answer", "explanation"],
        "example": {
            "prompt": "Match each item on the left with the correct item on the right:",
            "question_data": {
                "left_items": ["Item 1", "Item 2", "Item 3"],
                "right_items": ["Description A", "Description B", "Description C"],
            },
            "answer": "Item 1-Description B, Item 2-Description C, Item 3-Description A",
            "explanation": "Why these matches are correct",
        },
        "starter": (
            "Based on the following material, create matching questions for "
            "elementary students. Write everything in English.\n\n"
            "Material:\n{context}\n\n"
            "Requirements:\n"
            "1. Provide 3-5 items on the left with the same number of matches on the right\n"
            "2. Matches can be term-definition, cause-effect, item-category, etc.\n"
            "3. Keep matches clear and unambiguous; age-appropriate"
        ),
    },
    "sequence": {
        "label": "Sequencing",
        "required": ["prompt", "items", "answer", "explanation"],
        "example": {
            "prompt": "Put the following items in the correct order:",
            "items": ["Third step", "First step", "Fourth step", "Second step"],
            "answer": ["First step", "Second step", "Third step", "Fourth step"],
            "explanation": "Why this is the correct order",
        },
        "starter": (
            "Based on the following material, create sequencing (ordering) questions for "
            "elementary students. Write everything in English.\n\n"
            "Material:\n{context}\n\n"
            "Requirements:\n"
            "1. Provide 3-5 steps or items to order\n"
            "2. Present them in a scrambled order in the question (time, process, size, etc.)\n"
            "3. Give the correct order in the answer and explain the logic"
        ),
    },
    "enumeration": {
        "label": "Enumeration",
        "required": ["prompt", "answer", "explanation"],
        "example": {
            "prompt": "List three examples of a given topic:",
            "answer": ["First item", "Second item", "Third item"],
            "explanation": "Why these are correct, and any acceptable alternatives",
        },
        "starter": (
            "Based on the following material, create enumeration (listing) questions for "
            "elementary students. Write everything in English.\n\n"
            "Material:\n{context}\n\n"
            "Requirements:\n"
            '1. Ask students to list specific items (e.g., "List three...") and specify how '
            "many (usually 3-5)\n"
            "2. Items should be clearly found in the material\n"
            "3. Provide the complete list in the answer; age-appropriate"
        ),
    },
}


def build_format_instruction(question_type: Optional[str]) -> Optional[str]:
    """依 question_type 產生要注入 prompt 的「輸出格式指示」。

    回傳一段權威、明確的英文指示 + JSON 範例;未收錄的題型回 None
    (由呼叫端 fallback 到既有 _TYPE_HINTS)。
    """
    spec = QUESTION_TYPE_REGISTRY.get(question_type or "")
    if not spec:
        return None
    example = json.dumps(spec["example"], ensure_ascii=False, indent=2)
    required = ", ".join(spec["required"])
    return (
        "[OUTPUT FORMAT — follow strictly]\n"
        "Output only a single JSON array — no extra text, headings, or markdown fences.\n"
        f"Each object in the array must contain exactly these fields: {required}.\n"
        "Format each object like this example:\n"
        f"[\n{example}\n]"
    )


def list_starters() -> List[Dict[str, Any]]:
    """給前端題型範本庫 / 自動帶入的資料。"""
    return [
        {
            "question_type": key,
            "label": spec["label"],
            "required": spec["required"],
            "output_example": spec["example"],
            "starter_prose": spec["starter"],
        }
        for key, spec in QUESTION_TYPE_REGISTRY.items()
    ]
