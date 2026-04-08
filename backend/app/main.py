import uvicorn
from fastapi import FastAPI
from app.core.config import USE_MOCK_API, CORS_ORIGINS
from app.db.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="EduRAG Backend", debug=True)

# CORS 設定（來源清單由 config.py 從環境變數 CORS_ORIGINS 讀取）
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有方法，包括 OPTIONS
    allow_headers=["*"],
 )
# 只有在真實模式才自動建立資料表
if not USE_MOCK_API:
    @app.on_event("startup")
    async def on_startup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

# 註冊路由
from app.routers import health
app.include_router(health.router)

# 根據Mock模式決定使用哪個路由實現
if USE_MOCK_API:
    from app.routers.mock_ingest import router as ingest_router
    from app.routers.mock_generate import router as generate_router
    from app.routers.mock_questions import router as questions_router
    from app.routers.mock_templates import router as templates_router
    from app.routers.mock_dashboard import router as dashboard_router
    
    app.include_router(ingest_router)
    app.include_router(generate_router)
    app.include_router(questions_router)
    app.include_router(templates_router)
    app.include_router(dashboard_router)
else:
    from app.routers import ingest, generate, templates, documents, upload, dashboard, questions, subjects, image_questions, images
    app.include_router(ingest.router)
    app.include_router(generate.router)
    app.include_router(templates.router)
    app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
    app.include_router(upload.router)
    app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
    app.include_router(questions.router, prefix="/api/questions", tags=["questions"])
    app.include_router(subjects.router, tags=["subjects"])
    app.include_router(image_questions.router)
    app.include_router(images.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
