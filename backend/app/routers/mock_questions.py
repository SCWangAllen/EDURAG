from fastapi import APIRouter
from app.schemas.question import QuestionItem, QuestionType, QuestionSource

router = APIRouter(prefix="/api/mock/questions", tags=["mock"])

@router.get("/{id}", response_model=QuestionItem)
async def mock_get_question(id: int):
    return QuestionItem(
        type=QuestionType.SINGLE_CHOICE,
        prompt="示範題幹",
        options=["A. 選項一","B. 選項二","C. 選項三","D. 選項四"],
        answer="A",
        explanation="示範解析",
        source=QuestionSource(
            document_id=999,
            chunk_id=1001,
            chunk_text="這是示範的來源文本..."
        )
    )
