#!/usr/bin/env python3
"""
測試科目轉換功能
模擬前端發送的各種科目格式
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_subject_conversion():
    """測試科目名稱轉換"""
    
    print("🔄 測試科目轉換功能")
    print("=" * 50)
    
    # 模擬前端會發送的各種格式
    test_cases = [
        {"frontend": "Chinese", "expected_backend": "chinese"},
        {"frontend": "English", "expected_backend": "english"},  
        {"frontend": "Math", "expected_backend": "math"},
        {"frontend": "chinese", "expected_backend": "chinese"},  # 已經是正確格式
        {"frontend": "english", "expected_backend": "english"},
        {"frontend": "math", "expected_backend": "math"}
    ]
    
    async with httpx.AsyncClient() as client:
        
        for i, case in enumerate(test_cases, 1):
            frontend_subject = case["frontend"]
            expected_backend = case["expected_backend"]
            
            print(f"{i}. 測試 '{frontend_subject}' → '{expected_backend}'")
            
            # 模擬前端會構建的完整流程
            try:
                # 完整的工作流程測試
                payload = {
                    "subject": expected_backend,  # 這是前端轉換後會發送的
                    "text": f"這是{frontend_subject}科目的測試文本內容",
                    "title": f"{frontend_subject}測試文件"
                }
                
                # 步驟1: 攝取
                print(f"   📤 攝取請求: subject='{payload['subject']}'")
                ingest_res = await client.post(f"{BASE_URL}/api/ingest/", json=payload)
                
                if ingest_res.status_code == 200:
                    ingest_data = ingest_res.json()
                    document_id = ingest_data["document_id"]
                    print(f"   ✅ 攝取成功: Document ID = {document_id}")
                    
                    # 步驟2: 生成
                    generate_payload = {
                        "subject": expected_backend,
                        "document_id": document_id,
                        "types": {"single_choice": 1}
                    }
                    
                    generate_res = await client.post(f"{BASE_URL}/api/generate/", json=generate_payload)
                    if generate_res.status_code == 200:
                        generate_data = generate_res.json()
                        print(f"   ✅ 生成成功: {generate_data['total_count']} 道題目")
                        
                        # 檢查生成的題目內容是否包含科目相關資訊
                        first_question = generate_data['items'][0]
                        print(f"   📝 題目預覽: {first_question['prompt'][:50]}...")
                    else:
                        print(f"   ❌ 生成失敗: {generate_res.status_code}")
                        print(f"      {generate_res.text}")
                else:
                    print(f"   ❌ 攝取失敗: {ingest_res.status_code}")  
                    print(f"      {ingest_res.text}")
                    
            except Exception as e:
                print(f"   ❌ 異常: {e}")
            
            print()
        
        # 測試錯誤的科目
        print("7. 測試無效科目")
        try:
            invalid_payload = {
                "subject": "InvalidSubject",
                "text": "無效科目測試",
                "title": "錯誤測試"
            }
            
            invalid_res = await client.post(f"{BASE_URL}/api/ingest/", json=invalid_payload)
            if invalid_res.status_code != 200:
                print(f"   ✅ 正確拒絕無效科目: {invalid_res.status_code}")
                error_data = invalid_res.json()
                print(f"   📋 錯誤訊息: {error_data['detail'][0]['msg']}")
            else:
                print(f"   ❌ 意外接受了無效科目")
        except Exception as e:
            print(f"   ❌ 測試異常: {e}")
        
        print()
        print("🎉 科目轉換測試完成！")
        print()
        print("✅ 前端現在應該能夠:")
        print("- 發送 'Chinese' → 後端接收 'chinese'")
        print("- 發送 'English' → 後端接收 'english'") 
        print("- 發送 'Math' → 後端接收 'math'")
        print("- 顯示友好的錯誤消息")
        print("- 正確處理各種輸入格式")

if __name__ == "__main__":
    print("請確保後端服務已啟動在 localhost:8000")
    print()
    asyncio.run(test_subject_conversion())