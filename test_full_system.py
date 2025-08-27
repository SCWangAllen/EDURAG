#!/usr/bin/env python3
"""
完整系統測試 - 驗證前後端整合
測試Mock模式下的完整工作流程
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_full_workflow():
    """測試完整的前後端工作流程"""
    
    print("🧪 EduRAG 完整系統測試")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # 1. 健康檢查
        print("1. 健康檢查...")
        try:
            health_res = await client.get(f"{BASE_URL}/health")
            health_data = health_res.json()
            print(f"   ✅ 狀態: {health_data['status']}")
            print(f"   📊 模式: {health_data['mode']}")
            print(f"   🐍 Python: {health_data['python_version']}")
            assert health_res.status_code == 200
        except Exception as e:
            print(f"   ❌ 健康檢查失敗: {e}")
            return False
        
        print()
        
        # 2. 文件攝取測試（模擬前端第一步）
        print("2. 文件攝取測試...")
        ingest_payload = {
            "subject": "chinese",
            "text": "春天是萬物復甦的季節。樹木抽出新芽，花朵競相綻放。農夫開始忙碌地播種，希望秋天能夠豐收。春雨滋潤大地，為所有生物帶來生命的活力。在這個美好的季節裡，人們也充滿了希望和活力。",
            "title": "春天的美好"
        }
        
        try:
            ingest_res = await client.post(f"{BASE_URL}/api/ingest", json=ingest_payload)
            if ingest_res.status_code == 200:
                ingest_data = ingest_res.json()
                document_id = ingest_data["document_id"]
                print(f"   ✅ 攝取成功: Document ID = {document_id}")
                print(f"   📝 文本塊: {ingest_data['total_chunks']} 個")
                print(f"   ⏱️  耗時: {ingest_data['processing_time']:.3f}s")
            else:
                print(f"   ❌ 攝取失敗: {ingest_res.status_code} - {ingest_res.text}")
                return False
        except Exception as e:
            print(f"   ❌ 攝取異常: {e}")
            return False
        
        print()
        
        # 3. 題目生成測試（模擬前端第二步）
        print("3. 題目生成測試...")
        generate_payload = {
            "subject": "chinese",
            "document_id": document_id,
            "types": {
                "single_choice": 2,
                "cloze": 1,
                "short_answer": 1
            }
        }
        
        try:
            generate_res = await client.post(f"{BASE_URL}/api/generate", json=generate_payload)
            if generate_res.status_code == 200:
                generate_data = generate_res.json()
                print(f"   ✅ 生成成功: {generate_data['total_count']} 道題目")
                print(f"   ⏱️  耗時: {generate_data['generation_time']:.3f}s")
                
                # 顯示生成的題目
                print("\n4. 生成的題目預覽:")
                print("-" * 40)
                
                for i, item in enumerate(generate_data['items'][:3], 1):
                    type_map = {
                        'single_choice': '單選題',
                        'cloze': '填空題',
                        'short_answer': '簡答題'
                    }
                    
                    print(f"\n   題目 {i} ({type_map.get(item['type'], item['type'])})")
                    print(f"   題幹: {item['prompt']}")
                    
                    if item['options']:
                        print("   選項:")
                        for option in item['options']:
                            print(f"     {option}")
                    
                    print(f"   答案: {item['answer']}")
                    print(f"   解釋: {item['explanation']}")
                    print(f"   來源: 文件 {item['source']['document_id']}, 塊 {item['source']['chunk_id']}")
                    
                    # 前端格式轉換測試
                    frontend_format = {
                        'question': item['prompt'],
                        'options': item['options'],
                        'answer': item['answer'],
                        'explanation': item['explanation'],
                        'type': item['type'],
                        'context': item['source']['chunk_text'],
                        'source': item['source']
                    }
                    print(f"   ✅ 前端格式轉換: OK")
                
            else:
                print(f"   ❌ 生成失敗: {generate_res.status_code} - {generate_res.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ 生成異常: {e}")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 完整系統測試通過！")
        print("\n✅ 驗證項目:")
        print("- 健康檢查端點正常")
        print("- 文件攝取API正常")
        print("- 題目生成API正常")
        print("- API回應格式符合前端期望")
        print("- Mock模式運行穩定")
        
        print("\n🚀 系統已準備好前端連接!")
        print("前端可以直接調用 /api/ingest 和 /api/generate")
        
        return True

async def test_api_compatibility():
    """測試API相容性"""
    print("\n🔄 API相容性測試...")
    
    # 模擬前端的舊格式請求
    old_format_payload = {
        "subject": "chinese",
        "text": "測試文本內容。",
        "types": [
            {"type": "single_choice", "num": 2},
            {"type": "cloze", "num": 1}
        ]
    }
    
    # 這應該通過前端的useQuestions.js處理
    print("   ⚠️  前端舊格式相容性需要在瀏覽器中測試")
    return True

if __name__ == "__main__":
    print("請確保後端服務已啟動：")
    print("cd backend && USE_MOCK_API=true uvicorn app.main:app --reload")
    print()
    
    try:
        result = asyncio.run(test_full_workflow())
        if result:
            asyncio.run(test_api_compatibility())
        else:
            print("❌ 系統測試失敗，請檢查後端服務狀態")
    except KeyboardInterrupt:
        print("\n⚠️  測試中斷")
    except Exception as e:
        print(f"❌ 測試異常: {e}")
        import traceback
        traceback.print_exc()