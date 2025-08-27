#!/usr/bin/env python3
"""
快速測試腳本 - 直接導入模組測試API功能
無需啟動伺服器，直接測試Mock模式下的核心功能
"""

import asyncio
import os
import sys

# 設置環境變數為Mock模式
os.environ['USE_MOCK_API'] = 'true'
os.environ['DATABASE_URL'] = 'mock://localhost'
os.environ['OPENAI_API_KEY'] = 'mock-key'

# 添加當前目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_schemas():
    """測試Schema定義"""
    print("🧪 測試 Schema 定義...")
    
    from app.schemas.question import QuestionType, Subject, GenerateRequest, QuestionItem, QuestionSource
    from app.schemas.ingest import IngestRequest, IngestResponse, ChunkInfo
    
    # 測試生成請求
    generate_req = GenerateRequest(
        subject=Subject.CHINESE,
        document_id=999,
        types={
            QuestionType.SINGLE_CHOICE: 2,
            QuestionType.CLOZE: 1
        }
    )
    print(f"✅ GenerateRequest: {generate_req.subject}, {len(generate_req.types)} 種題型")
    
    # 測試攝取請求  
    ingest_req = IngestRequest(
        subject=Subject.CHINESE,
        text="這是測試文本內容，包含多個句子用於測試分塊功能。",
        title="測試文件"
    )
    print(f"✅ IngestRequest: {ingest_req.subject}, 文本長度 {len(ingest_req.text)}")
    
    print()

async def test_mock_functions():
    """測試Mock功能"""
    print("🎭 測試 Mock 功能...")
    
    from app.core.llm_client import generate_questions_by_type
    from app.schemas.question import QuestionType, Subject
    
    # 測試Mock LLM生成
    questions = await generate_questions_by_type(
        context="測試課文內容",
        question_type=QuestionType.SINGLE_CHOICE,
        count=2,
        subject=Subject.CHINESE
    )
    
    print(f"✅ Mock LLM 生成了 {len(questions)} 道題目")
    for i, q in enumerate(questions, 1):
        print(f"   題目 {i}: {q['prompt'][:30]}...")
    
    print()

async def test_health_response():
    """測試健康檢查回應結構"""
    print("💓 測試健康檢查...")
    
    from app.routers.health import HealthResponse
    from datetime import datetime
    
    health = HealthResponse(
        status="healthy",
        version="1.0.0", 
        timestamp=datetime.now(),
        mode="mock",
        database_connected=True,
        python_version="3.12.8"
    )
    
    print(f"✅ Health Response: {health.status}, {health.mode} 模式")
    print()

async def main():
    """主測試流程"""
    print("🚀 EduRAG Backend 快速測試\n")
    print("=" * 50)
    
    try:
        await test_schemas()
        await test_mock_functions() 
        await test_health_response()
        
        print("🎉 所有測試通過！")
        print("\n💡 系統已準備就緒，可以啟動API伺服器：")
        print("   USE_MOCK_API=true uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())