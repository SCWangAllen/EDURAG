#!/usr/bin/env python3
"""
測試 Claude API 整合的簡單腳本
使用前請先設定環境變數：
- LLM_PROVIDER=anthropic
- ANTHROPIC_API_KEY=your-claude-api-key
"""

import asyncio
import os
import sys
from pathlib import Path

# 加入專案路徑以便匯入模組
sys.path.insert(0, str(Path(__file__).parent))

async def test_claude_integration():
    """測試 Claude API 整合"""
    
    # 設定測試環境變數
    os.environ["USE_MOCK_API"] = "false"
    os.environ["LLM_PROVIDER"] = "anthropic"
    
    # 檢查 API Key 是否設定
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ 請先設定 ANTHROPIC_API_KEY 環境變數")
        return False
    
    try:
        # 匯入相關模組
        from app.core.llm_client import generate_questions_by_type
        from app.schemas.question import QuestionType, Subject
        
        print("✅ 成功匯入相關模組")
        
        # 測試資料
        test_context = """
        人工智慧是一門讓機器表現出類似人類智慧行為的科學技術。
        它包含機器學習、深度學習、自然語言處理等多個領域。
        近年來，AI 在醫療診斷、自動駕駛、語音辨識等方面都有重大突破。
        """
        
        # 測試生成單選題
        print("\n🧪 開始測試生成單選題...")
        questions = await generate_questions_by_type(
            context=test_context,
            question_type=QuestionType.SINGLE_CHOICE,
            count=2,
            subject=Subject.HEALTH
        )
        
        print(f"✅ 成功生成 {len(questions)} 道單選題")
        for i, q in enumerate(questions, 1):
            print(f"  題目 {i}: {q.get('prompt', 'N/A')[:50]}...")
        
        # 測試生成簡答題
        print("\n🧪 開始測試生成簡答題...")
        questions = await generate_questions_by_type(
            context=test_context,
            question_type=QuestionType.SHORT_ANSWER,
            count=1,
            subject=Subject.ENGLISH
        )
        
        print(f"✅ 成功生成 {len(questions)} 道簡答題")
        for i, q in enumerate(questions, 1):
            print(f"  題目 {i}: {q.get('prompt', 'N/A')[:50]}...")
            
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_openai_integration():
    """測試 OpenAI API 整合（對照測試）"""
    
    # 設定測試環境變數
    os.environ["USE_MOCK_API"] = "false"
    os.environ["LLM_PROVIDER"] = "openai"
    
    # 檢查 API Key 是否設定
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  未設定 OPENAI_API_KEY，跳過 OpenAI 測試")
        return True
    
    try:
        # 匯入相關模組
        from app.core.llm_client import generate_questions_by_type
        from app.schemas.question import QuestionType, Subject
        
        # 測試資料
        test_context = """
        Python 是一種高階程式語言，具有簡潔易讀的語法。
        它廣泛應用於網頁開發、資料科學、人工智慧等領域。
        Python 支援物件導向、函數式和程序式程式設計範式。
        """
        
        print("\n🧪 開始測試 OpenAI 生成題目...")
        questions = await generate_questions_by_type(
            context=test_context,
            question_type=QuestionType.CLOZE,
            count=1,
            subject=Subject.ENGLISH
        )
        
        print(f"✅ OpenAI 成功生成 {len(questions)} 道題目")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI 測試失敗: {e}")
        return False

async def main():
    """主測試函數"""
    print("🚀 開始 LLM 整合測試")
    print("=" * 50)
    
    # 測試 Claude 整合
    claude_success = await test_claude_integration()
    
    # 測試 OpenAI 整合（對照）
    openai_success = await test_openai_integration()
    
    print("\n" + "=" * 50)
    print("📊 測試結果總結:")
    print(f"  Claude API: {'✅ 通過' if claude_success else '❌ 失敗'}")
    print(f"  OpenAI API: {'✅ 通過' if openai_success else '❌ 失敗'}")
    
    if claude_success:
        print("\n🎉 Claude API 整合成功！")
        print("使用方式：")
        print("  1. 在 .env 中設定 LLM_PROVIDER=anthropic")
        print("  2. 在 .env 中設定 ANTHROPIC_API_KEY=your-key")
        print("  3. 重啟服務即可使用 Claude API")

if __name__ == "__main__":
    asyncio.run(main())