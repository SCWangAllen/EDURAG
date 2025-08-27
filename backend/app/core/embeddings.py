# app/core/embeddings.py
from app.core.config import USE_MOCK_API, OPENAI_API_KEY

if not USE_MOCK_API:
    # 真實模式：載入 OpenAI client 並呼叫 embeddings API
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    async def create_embedding(text: str) -> list[float]:
        resp = await client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return resp.data[0].embedding

else:
    # Mock 模式：回傳固定零向量（長度對應 1536）
    async def create_embedding(text: str) -> list[float]:
        return [0.0] * 1536
