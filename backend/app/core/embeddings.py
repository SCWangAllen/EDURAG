# app/core/embeddings.py
from app.core.config import USE_MOCK_API, ANTHROPIC_API_KEY

if not USE_MOCK_API:
    # 真實模式：使用 Claude 進行文本嵌入（實際上 Claude 不提供嵌入服務，所以使用 Mock）
    # 注意：Anthropic 不提供嵌入服務，這裡實際返回 Mock 數據
    async def create_embedding(text: str) -> list[float]:
        # Claude 沒有嵌入服務，使用固定向量或其他嵌入服務
        # 為了簡化，這裡返回基於文本長度的簡單向量
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        # 生成一個基於哈希的 1536 維向量
        embedding = []
        for i in range(1536):
            embedding.append(float(int(text_hash[i % len(text_hash)], 16) / 15.0 - 0.5))
        return embedding

else:
    # Mock 模式：回傳固定零向量（長度對應 1536）
    async def create_embedding(text: str) -> list[float]:
        return [0.0] * 1536
