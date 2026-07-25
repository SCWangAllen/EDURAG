"""題型單一真實來源(single source of truth)。

每個題型集中定義:顯示名、必填欄位、輸出 JSON 範例、起始模版(純指示語)。
用途:
  1. 生成時依 `question_type` 由後端**自動注入**輸出 JSON 格式(build_format_instruction),
     老師的模版只需寫「指示語」,不必手寫 JSON —— 避免寫錯 key 導致整批題目被丟、生成失敗。
  2. starter API(list_starters)給前端「題型範本庫」與 TemplateModal 選題型自動帶入。

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
        "label": "單選題",
        "required": ["prompt", "options", "answer", "explanation"],
        "example": {
            "prompt": "題目題幹",
            "options": ["A. 選項一", "B. 選項二", "C. 選項三", "D. 選項四"],
            "answer": "B",
            "explanation": "為什麼這個答案正確",
        },
        "starter": (
            "請根據以下教材,為國小學生出「單選題」。\n\n"
            "教材內容:\n{context}\n\n"
            "出題要求:\n"
            "1. 題幹清楚、用字符合國小程度\n"
            "2. 每題剛好 4 個選項(A、B、C、D),且只有一個正確答案\n"
            "3. 附上正確答案的簡短說明\n"
            "4. 緊扣教材重點,避免超出教材範圍"
        ),
    },
    "cloze": {
        "label": "填空題",
        "required": ["prompt", "answer", "explanation"],
        "example": {
            "prompt": "句子中用 ______ 標示要填入的空格",
            "answer": "正確答案",
            "explanation": "為什麼填這個答案",
        },
        "starter": (
            "請根據以下教材,為國小學生出「填空題」。\n\n"
            "教材內容:\n{context}\n\n"
            "出題要求:\n"
            "1. 用 ______ 標示要填的空格\n"
            "2. 每個空格測驗一個關鍵概念,句子要有足夠的上下文線索\n"
            "3. 聚焦重要詞彙與概念,難度適合國小學生"
        ),
    },
    "short_answer": {
        "label": "簡答題",
        "required": ["prompt", "answer", "explanation"],
        "example": {
            "prompt": "清楚、需要說明或描述的問題",
            "answer": "1 到 3 句的參考答案",
            "explanation": "好的答案應包含哪些重點",
        },
        "starter": (
            "請根據以下教材,為國小學生出「簡答題」。\n\n"
            "教材內容:\n{context}\n\n"
            "出題要求:\n"
            "1. 問題清楚、直接\n"
            "2. 參考答案約 1 到 3 句\n"
            "3. 測驗理解而非死背,難度適合國小學生\n"
            "4. 附上評分重點說明"
        ),
    },
    "true_false": {
        "label": "是非題",
        "required": ["prompt", "answer", "explanation"],
        "example": {
            "prompt": "一句明確為對或錯的敘述",
            "answer": "true",
            "explanation": "為什麼這句話是對的/錯的",
        },
        "starter": (
            "請根據以下教材,為國小學生出「是非題」。\n\n"
            "教材內容:\n{context}\n\n"
            "出題要求:\n"
            "1. 敘述清楚、明確,避免模稜兩可或陷阱題\n"
            "2. 測驗重要概念,而非枝微末節\n"
            "3. 附上判斷對錯的理由\n"
            '注意:答案必須恰好是 "true" 或 "false"(小寫)。'
        ),
    },
    "matching": {
        "label": "配對題",
        "required": ["prompt", "question_data", "answer", "explanation"],
        "example": {
            "prompt": "請將左欄與右欄正確配對:",
            "question_data": {
                "left_items": ["項目一", "項目二", "項目三"],
                "right_items": ["敘述 A", "敘述 B", "敘述 C"],
            },
            "answer": "項目一-敘述 B, 項目二-敘述 C, 項目三-敘述 A",
            "explanation": "為什麼這些配對正確",
        },
        "starter": (
            "請根據以下教材,為國小學生出「配對題」。\n\n"
            "教材內容:\n{context}\n\n"
            "出題要求:\n"
            "1. 左欄 3 到 5 個項目,右欄提供相同數量的對應項\n"
            "2. 配對可為:詞彙-定義、原因-結果、項目-類別等\n"
            "3. 配對關係清楚、無歧義,難度適合國小學生"
        ),
    },
    "sequence": {
        "label": "排序題",
        "required": ["prompt", "items", "answer", "explanation"],
        "example": {
            "prompt": "請將下列項目排成正確順序:",
            "items": ["第三步", "第一步", "第四步", "第二步"],
            "answer": ["第一步", "第二步", "第三步", "第四步"],
            "explanation": "為什麼這是正確順序",
        },
        "starter": (
            "請根據以下教材,為國小學生出「排序題」。\n\n"
            "教材內容:\n{context}\n\n"
            "出題要求:\n"
            "1. 提供 3 到 5 個需要排序的步驟或項目\n"
            "2. 依邏輯順序(時間、流程、大小等),題目中以打亂的順序呈現\n"
            "3. 答案給出正確順序,並說明排序邏輯"
        ),
    },
    "enumeration": {
        "label": "列舉題",
        "required": ["prompt", "answer", "explanation"],
        "example": {
            "prompt": "請列舉三項「某主題」的例子:",
            "answer": ["項目一", "項目二", "項目三"],
            "explanation": "為什麼這些是正確答案,以及可接受的其他答案",
        },
        "starter": (
            "請根據以下教材,為國小學生出「列舉題」。\n\n"
            "教材內容:\n{context}\n\n"
            "出題要求:\n"
            "1. 請學生列舉特定項目(例如「列舉三種…」),並指定數量(通常 3 到 5 項)\n"
            "2. 答案項目要能清楚從教材中找到\n"
            "3. 提供完整答案清單,難度適合國小學生"
        ),
    },
}


def build_format_instruction(question_type: Optional[str]) -> Optional[str]:
    """依 question_type 產生要注入 prompt 的「輸出格式指示」。

    回傳一段權威、明確的中文指示 + JSON 範例;未收錄的題型回 None
    (由呼叫端 fallback 到既有 _TYPE_HINTS)。
    """
    spec = QUESTION_TYPE_REGISTRY.get(question_type or "")
    if not spec:
        return None
    example = json.dumps(spec["example"], ensure_ascii=False, indent=2)
    required = "、".join(spec["required"])
    return (
        "【輸出格式(務必嚴格遵守)】\n"
        "只輸出一個 JSON 陣列,不要輸出任何多餘文字、標題或 markdown 圍欄。\n"
        f"陣列中每個物件必須且只包含這些欄位:{required}。\n"
        "每個物件的格式範例如下:\n"
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
