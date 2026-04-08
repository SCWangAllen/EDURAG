# app/db/database.py
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import DATABASE_URL, USE_MOCK_API

# 無論 mock 或真實模式，都要有 Base 讓 models.py 能正常繼承
Base = declarative_base()

if not USE_MOCK_API:
    # 真實模式：初始化資料庫連線
    engine = create_async_engine(DATABASE_URL, echo=True)
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def get_db():
        async with AsyncSessionLocal() as session:
            yield session

else:
    # Mock 模式：不建立任何 DB 連線，呼叫 get_db 時回 503
    engine = None
    AsyncSessionLocal = None

    async def get_db():
        raise HTTPException(status_code=503, detail="Mock 模式：DB 不可用")
