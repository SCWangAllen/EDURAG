from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
import psycopg, json

QuestionType = Literal["single_choice", "cloze", "short_answer"]

class GenReq(BaseModel):
    doc_id: int
    subject: str
    question_type: QuestionType
    count: int = 5

router = APIRouter()

SYSTEM = """你是一位高中{subject}教師。
根據以下<內容>，請依 {question_type} 類型產生 {count} 題，
每題必須含「題幹、(若適用)選項、答案、解析」，回傳 JSON 陣列。

<內容>
{context}
"""

@router.post("/", status_code=201)
async def generate(r: GenReq):
    conn = psycopg.connect(row_factory=psycopg.rows.dict_row)
    ctx_rows = conn.execute(
        "SELECT chunk_text FROM embeddings WHERE doc_id=%s LIMIT 6",
        (r.doc_id,)
    ).fetchall()
    context = "\n".join(row["chunk_text"] for row in ctx_rows)

    prompt = PromptTemplate.from_template(SYSTEM)
    llm = OpenAI(model="gpt-4o-mini")
    raw = llm.invoke(prompt.format(**r.dict(), context=context))
    questions = json.loads(raw)

    return {"questions": questions}
