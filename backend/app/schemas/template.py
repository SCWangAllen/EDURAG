from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class TemplateBase(BaseModel):
    subject_id: Optional[int] = Field(None, description="科目ID")
    subject: Optional[str] = Field(None, description="科目名稱（兼容性）")
    name: str = Field(..., max_length=100, description="模板名稱")
    content: str = Field(..., description="Prompt 模板內容")
    question_type: Optional[str] = Field(None, description="題型")
    params: Optional[Dict[str, Any]] = Field(None, description="LLM 參數設定")

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    subject_id: Optional[int] = Field(None, description="科目ID")
    name: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = Field(None)
    question_type: Optional[str] = Field(None, description="題型")
    params: Optional[Dict[str, Any]] = Field(None)
    is_active: Optional[bool] = Field(None, description="是否啟用")

class TemplateResponse(BaseModel):
    id: int
    subject_id: Optional[int]
    subject: str  # 科目名稱（從關聯或舊欄位取得）
    name: str
    content: str
    question_type: Optional[str] = Field(None, description="題型")
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

# Question Type JSON Schema Definitions
# 定義每種題型的 JSON 回應格式規範
QUESTION_TYPE_SCHEMAS = {
    'single_choice': {
        'required': ['prompt', 'options', 'answer', 'explanation'],
        'format': {
            'prompt': 'Question stem as string',
            'options': 'Array of 4 strings (A-D options)',
            'answer': 'Single letter (A/B/C/D) or full option text',
            'explanation': 'String explaining the correct answer'
        },
        'example': {
            "prompt": "What is the primary function of the heart?",
            "options": ["A. Digest food", "B. Pump blood", "C. Filter air", "D. Store energy"],
            "answer": "B",
            "explanation": "The heart pumps blood throughout the body via the circulatory system."
        }
    },
    'cloze': {
        'required': ['prompt', 'answer', 'explanation'],
        'format': {
            'prompt': 'String with ______ marking blank spaces',
            'answer': 'String or array of correct words',
            'explanation': 'String explaining the answer'
        },
        'example': {
            "prompt": "The heart pumps ______ throughout the body.",
            "answer": "blood",
            "explanation": "The heart's primary function is to circulate blood through the circulatory system."
        }
    },
    'short_answer': {
        'required': ['prompt', 'answer', 'explanation'],
        'format': {
            'prompt': 'Question string',
            'answer': 'Expected answer string (2-3 sentences)',
            'explanation': 'Detailed explanation'
        },
        'example': {
            "prompt": "Explain how the heart works.",
            "answer": "The heart is a muscle that pumps blood. It has four chambers that work together to circulate blood throughout the body.",
            "explanation": "A complete answer should mention the heart's muscular nature, pumping action, and circulatory function."
        }
    },
    'true_false': {
        'required': ['prompt', 'answer', 'explanation'],
        'format': {
            'prompt': 'Statement string',
            'answer': 'Boolean as "true" or "false" string',
            'explanation': 'String explaining why the statement is true/false'
        },
        'example': {
            "prompt": "The heart has four chambers.",
            "answer": "true",
            "explanation": "The heart consists of four chambers: two atria and two ventricles."
        }
    },
    'matching': {
        'required': ['prompt', 'question_data', 'answer', 'explanation'],
        'format': {
            'prompt': 'Matching instruction string',
            'question_data': 'Object with left_items and right_items arrays',
            'answer': 'String describing correct pairs',
            'explanation': 'String explaining the matches'
        },
        'example': {
            "prompt": "Match each organ with its function:",
            "question_data": {
                "left_items": ["Heart", "Lungs", "Stomach"],
                "right_items": ["Digests food", "Pumps blood", "Exchanges oxygen"]
            },
            "answer": "Heart-Pumps blood, Lungs-Exchanges oxygen, Stomach-Digests food",
            "explanation": "Each organ has a specific primary function in the body system."
        }
    },
    'sequence': {
        'required': ['prompt', 'items', 'answer', 'explanation'],
        'format': {
            'prompt': 'Sequencing instruction string',
            'items': 'Array of items in random order',
            'answer': 'Array of items in correct order or string describing sequence',
            'explanation': 'String explaining the correct sequence'
        },
        'example': {
            "prompt": "Arrange these steps of blood circulation in correct order:",
            "items": ["Blood returns to heart", "Heart pumps blood", "Blood reaches body tissues", "Blood gets oxygen in lungs"],
            "answer": ["Blood gets oxygen in lungs", "Heart pumps blood", "Blood reaches body tissues", "Blood returns to heart"],
            "explanation": "Blood circulation follows a cycle: oxygenation, pumping, delivery, and return."
        }
    },
    'enumeration': {
        'required': ['prompt', 'answer', 'explanation'],
        'format': {
            'prompt': 'Question asking to list items',
            'answer': 'Array of correct items',
            'explanation': 'String explaining the list'
        },
        'example': {
            "prompt": "List three main functions of the circulatory system:",
            "answer": ["Transport oxygen", "Remove waste", "Deliver nutrients"],
            "explanation": "The circulatory system has multiple critical functions that maintain body health."
        }
    },
    'symbol_identification': {
        'required': ['prompt', 'symbols', 'answer', 'explanation'],
        'format': {
            'prompt': 'Identification instruction string',
            'symbols': 'Array of symbol descriptions or identifiers',
            'answer': 'Correct symbol name or meaning',
            'explanation': 'String explaining the symbol'
        },
        'example': {
            "prompt": "What does the ♥ symbol represent in health education?",
            "symbols": ["♥", "⚕", "❤️"],
            "answer": "Heart or cardiovascular health",
            "explanation": "The heart symbol is universally recognized to represent cardiac health and the circulatory system."
        }
    }
}

# Default Template Configurations (English Version)
# 預設模板配置（英文版）
DEFAULT_TEMPLATES = {
    "Health": {
        "single_choice": {
            "content": """Based on the following educational content, create multiple-choice questions for elementary students.

Educational Content:
{context}

Please create multiple-choice questions with these requirements:
1. Question stem should be clear and age-appropriate
2. Provide exactly 4 options labeled A, B, C, D
3. One correct answer must be clearly identifiable
4. Include explanation for the correct answer

Make questions appropriate for elementary school level (grades 1-6).

Return in JSON format:
[
  {{
    "prompt": "Question stem asking about the content",
    "options": ["A. First option", "B. Second option", "C. Third option", "D. Fourth option"],
    "answer": "B",
    "explanation": "Why this answer is correct"
  }}
]""",
            "params": {"temperature": 0.7, "max_tokens": 1000, "top_p": 1.0, "frequency_penalty": 0.0},
            "question_type": "single_choice"
        },
        "cloze": {
            "content": """Based on the following educational content, create fill-in-the-blank questions for elementary students.

Educational Content:
{context}

Please create cloze questions with these requirements:
1. Use ______ to mark blank spaces
2. Each blank should test one key concept
3. Provide clear context clues in the sentence
4. Make blanks appropriate difficulty for young learners
5. Focus on important vocabulary and concepts

Generate fill-in-the-blank questions using blanks for missing words. Return in JSON format:
[
  {{
    "prompt": "Sentence with ______ marking the blank space to fill",
    "answer": "correct word or phrase",
    "explanation": "Why this word fits in the context"
  }}
]""",
            "params": {"temperature": 0.7, "max_tokens": 1000, "top_p": 1.0, "frequency_penalty": 0.0},
            "question_type": "cloze"
        },
        "short_answer": {
            "content": """Based on the following educational content, create short answer questions for elementary students.

Educational Content:
{context}

Please create short answer questions with these requirements:
1. Ask clear, direct questions
2. Expected answers should be 1-3 sentences long
3. Questions should test understanding, not just memory
4. Make age-appropriate for elementary students
5. Provide a model answer and grading explanation

Return in JSON format:
[
  {{
    "prompt": "Clear question asking for explanation or description",
    "answer": "Model answer in 1-3 complete sentences",
    "explanation": "What key points should be included in a good answer"
  }}
]""",
            "params": {"temperature": 0.7, "max_tokens": 1200, "top_p": 1.0, "frequency_penalty": 0.0},
            "question_type": "short_answer"
        },
        "true_false": {
            "content": """Based on the following educational content, create true/false questions for elementary students.

Educational Content:
{context}

Please create true/false questions with these requirements:
1. Make clear, definitive statements
2. Avoid trick questions or ambiguous wording
3. Test important concepts, not trivial details
4. Provide clear explanation for why statement is true or false
5. Make age-appropriate for young learners

Return in JSON format:
[
  {{
    "prompt": "A clear statement that is either true or false",
    "answer": "true",
    "explanation": "Why this statement is true/false, with supporting details"
  }}
]

Note: Answer must be exactly "true" or "false" (lowercase).""",
            "params": {"temperature": 0.7, "max_tokens": 1000, "top_p": 1.0, "frequency_penalty": 0.0},
            "question_type": "true_false"
        },
        "matching": {
            "content": """Based on the following educational content, create matching questions for elementary students.

Educational Content:
{context}

Please create matching questions with these requirements:
1. Provide 3-5 items in left column to match
2. Provide corresponding items in right column
3. Items can be: terms-definitions, causes-effects, items-categories, etc.
4. Make clear and unambiguous matches
5. Age-appropriate for elementary students

Return in JSON format:
[
  {{
    "prompt": "Match each item on the left with the correct item on the right:",
    "question_data": {{
      "left_items": ["Item 1", "Item 2", "Item 3"],
      "right_items": ["Match A", "Match B", "Match C"]
    }},
    "answer": "Item 1-Match B, Item 2-Match C, Item 3-Match A",
    "explanation": "Why these matches are correct"
  }}
]""",
            "params": {"temperature": 0.7, "max_tokens": 1200, "top_p": 1.0, "frequency_penalty": 0.0},
            "question_type": "matching"
        },
        "sequence": {
            "content": """Based on the following educational content, create sequence ordering questions for elementary students.

Educational Content:
{context}

Please create sequence questions with these requirements:
1. Provide 3-5 steps or items to put in order
2. Items should follow a logical sequence (time, process, size, etc.)
3. Present items in scrambled order
4. Provide correct sequence in answer
5. Make age-appropriate for young learners

Return in JSON format:
[
  {{
    "prompt": "Put these items in the correct order:",
    "items": ["Third step", "First step", "Fourth step", "Second step"],
    "answer": ["First step", "Second step", "Third step", "Fourth step"],
    "explanation": "Why this is the correct sequence, explaining the logic"
  }}
]""",
            "params": {"temperature": 0.7, "max_tokens": 1200, "top_p": 1.0, "frequency_penalty": 0.0},
            "question_type": "sequence"
        },
        "enumeration": {
            "content": """Based on the following educational content, create enumeration (listing) questions for elementary students.

Educational Content:
{context}

Please create enumeration questions with these requirements:
1. Ask students to list specific items (e.g., "List 3 types of...")
2. Specify how many items to list (usually 3-5)
3. Items should be clearly identifiable from the content
4. Provide complete list in answer
5. Make age-appropriate for elementary students

Return in JSON format:
[
  {{
    "prompt": "List three [items/types/examples] of [topic]:",
    "answer": ["First item", "Second item", "Third item"],
    "explanation": "Why these items are correct examples, and any acceptable alternatives"
  }}
]""",
            "params": {"temperature": 0.7, "max_tokens": 1000, "top_p": 1.0, "frequency_penalty": 0.0},
            "question_type": "enumeration"
        },
        "symbol_identification": {
            "content": """Based on the following educational content, create symbol identification questions for elementary students.

Educational Content:
{context}

Please create symbol identification questions with these requirements:
1. Ask about symbols, signs, or visual representations
2. Provide 2-4 symbol options (can be text descriptions of symbols)
3. Test understanding of symbol meaning
4. Make culturally appropriate and age-appropriate
5. Include clear explanation of symbol significance

Return in JSON format:
[
  {{
    "prompt": "What does the [symbol description] represent?",
    "symbols": ["Symbol 1 description", "Symbol 2 description", "Symbol 3 description"],
    "answer": "Correct meaning or name of the symbol",
    "explanation": "What this symbol represents and why it's important"
  }}
]""",
            "params": {"temperature": 0.7, "max_tokens": 1000, "top_p": 1.0, "frequency_penalty": 0.0},
            "question_type": "symbol_identification"
        },
        "mixed": {
            "content": """Based on the following educational content, create a variety of different question types for elementary students.

Educational Content:
{context}

Please create mixed question types with these requirements:
1. Include multiple question formats (multiple choice, fill-in-blank, true/false, etc.)
2. Each question should use appropriate format
3. All questions should be age-appropriate
4. Include variety to test different skills
5. Mark each question's type in the response

Return in JSON format:
[
  {{
    "type": "single_choice",
    "prompt": "Question text",
    "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
    "answer": "B",
    "explanation": "Explanation text"
  }},
  {{
    "type": "true_false",
    "prompt": "Statement to evaluate",
    "answer": "true",
    "explanation": "Explanation text"
  }}
]""",
            "params": {"temperature": 0.8, "max_tokens": 1500, "top_p": 1.0, "frequency_penalty": 0.1},
            "question_type": "mixed"
        },
        "auto": {
            "content": """Based on the following educational content, automatically determine the most appropriate question type and create questions for elementary students.

Educational Content:
{context}

Please analyze the content and create questions using the most suitable format(s):
- Multiple choice for fact recall and concept understanding
- Fill-in-blank for vocabulary and key terms
- True/false for statement verification
- Short answer for explanation and description
- Other formats as appropriate

Requirements:
1. Choose question type that best fits the content
2. Make age-appropriate for elementary students (grades 1-6)
3. Test important concepts
4. Provide clear answers and explanations

Return in JSON format:
[
  {{
    "prompt": "Question text in appropriate format",
    "options": ["Only if multiple choice"],
    "answer": "Correct answer",
    "explanation": "Why this answer is correct"
  }}
]""",
            "params": {"temperature": 0.7, "max_tokens": 1500, "top_p": 1.0, "frequency_penalty": 0.0},
            "question_type": "auto"
        }
    }
}