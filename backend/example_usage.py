#!/usr/bin/env python3
"""
EduRAG API 使用範例
確保以Mock模式運行，展示完整的工作流程
"""

import asyncio
import httpx
import json

# 基礎設定
BASE_URL = "http://localhost:8000"

async def demonstrate_edurag_workflow():
    """示範EduRAG的完整工作流程"""
    
    print("🚀 EduRAG Mock API 示範開始\n")
    
    async with httpx.AsyncClient() as client:
        
        # 1. 健康檢查
        print("1. 檢查系統健康狀態")
        health_response = await client.get(f"{BASE_URL}/health")
        print(f"   狀態: {health_response.json()['status']}")
        print(f"   模式: {health_response.json()['mode']}")
        print()
        
        # 2. 文件攝取
        print("2. 攝取教材文件")
        ingest_payload = {
            "subject": "chinese",
            "text": "春天是萬物復甦的季節。樹木抽出新芽，花朵競相綻放。農夫開始忙碌地播種，希望秋天能夠豐收。春雨滋潤大地，為所有生物帶來生命的活力。在這個美好的季節裡，人們也充滿了希望和活力。",
            "title": "春天的美好"
        }
        
        ingest_response = await client.post(
            f"{BASE_URL}/api/ingest/", 
            json=ingest_payload
        )
        
        if ingest_response.status_code == 200:
            ingest_data = ingest_response.json()
            document_id = ingest_data["document_id"]
            print(f"   ✅ 文件已成功攝取")
            print(f"   📄 文件ID: {document_id}")
            print(f"   📝 文本塊數量: {ingest_data['total_chunks']}")
            print(f"   ⏱️  處理時間: {ingest_data['processing_time']:.2f}s")
        else:
            print(f"   ❌ 攝取失敗: {ingest_response.text}")
            return
        
        print()
        
        # 3. 生成題目
        print("3. 生成教學題目")
        generate_payload = {
            "subject": "chinese",
            "document_id": document_id,
            "types": {
                "single_choice": 2,
                "cloze": 1,
                "short_answer": 1
            }
        }
        
        generate_response = await client.post(
            f"{BASE_URL}/api/generate/",
            json=generate_payload
        )
        
        if generate_response.status_code == 200:
            generate_data = generate_response.json()
            print(f"   ✅ 題目已成功生成")
            print(f"   📊 總題數: {generate_data['total_count']}")
            print(f"   ⏱️  生成時間: {generate_data['generation_time']:.2f}s")
            print()
            
            # 顯示生成的題目
            print("4. 生成的題目內容:")
            print("=" * 50)
            
            for i, item in enumerate(generate_data['items'], 1):
                print(f"\n題目 {i} ({item['type']})")
                print(f"題幹: {item['prompt']}")
                
                if item['options']:
                    print("選項:")
                    for option in item['options']:
                        print(f"  {option}")
                
                print(f"答案: {item['answer']}")
                print(f"解釋: {item['explanation']}")
                print(f"來源: 文件ID {item['source']['document_id']}, 塊ID {item['source']['chunk_id']}")
                print(f"來源文本: {item['source']['chunk_text']}")
                print("-" * 30)
                
        else:
            print(f"   ❌ 生成失敗: {generate_response.text}")
    
    print("\n🎉 EduRAG Mock API 示範完成!")
    print("\n💡 提示:")
    print("- 此示範運行在Mock模式，使用預設的假資料")
    print("- 在正式環境中，需要設定PostgreSQL和OpenAI API金鑰")
    print("- 所有API回傳的資料結構在Mock和實際模式中完全一致")

if __name__ == "__main__":
    print("請確保後端服務已在 localhost:8000 啟動")
    print("啟動命令: cd backend && USE_MOCK_API=true uvicorn app.main:app --reload")
    print()
    
    asyncio.run(demonstrate_edurag_workflow())