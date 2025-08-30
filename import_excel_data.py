#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import asyncio
import asyncpg
import os
from datetime import datetime

# 資料庫連接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'edurag',
    'user': 'edurag_user',
    'password': 'edurag_password'
}

async def create_connection():
    """建立資料庫連接"""
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✅ 資料庫連接成功")
        return conn
    except Exception as e:
        print(f"❌ 資料庫連接失敗: {e}")
        return None

async def import_excel_to_db():
    """將 Excel 資料匯入資料庫"""
    
    # 讀取 Excel 檔案
    print("📖 讀取 Excel 檔案...")
    try:
        df = pd.read_excel('題目列表.xlsx', sheet_name='工作表1')
        print(f"✅ 成功讀取 {len(df)} 筆資料")
    except Exception as e:
        print(f"❌ 讀取 Excel 失敗: {e}")
        return
    
    # 建立資料庫連接
    conn = await create_connection()
    if not conn:
        return
    
    try:
        # 清空現有的文件資料 (可選)
        print("🗑️  清空現有文件資料...")
        await conn.execute("DELETE FROM documents WHERE import_source = 'excel_import'")
        
        # 開始匯入資料
        print("📥 開始匯入資料到 PostgreSQL...")
        imported_count = 0
        
        for index, row in df.iterrows():
            # 準備資料
            content = str(row['Words']) if pd.notna(row['Words']) else ''
            chapter = str(row['Chapter']) if pd.notna(row['Chapter']) else ''
            subject = str(row['Subject']) if pd.notna(row['Subject']) else '健康'
            image_filename = str(row['Imagesrelated']) if pd.notna(row['Imagesrelated']) else None
            
            # 生成標題（從章節或內容前100字）
            if chapter:
                title = chapter.split('\n')[0][:100] if '\n' in chapter else chapter[:100]
            else:
                title = content[:50] + '...' if len(content) > 50 else content
            
            # 插入資料
            try:
                await conn.execute("""
                    INSERT INTO documents (
                        title, content, subject, chapter, 
                        image_filename, import_source, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, 
                title.strip(),
                content,
                subject,
                chapter,
                image_filename,
                'excel_import',
                datetime.now()
                )
                imported_count += 1
                print(f"  ✅ 第 {imported_count} 筆: {title[:30]}...")
                
            except Exception as e:
                print(f"  ❌ 第 {index+1} 筆匯入失敗: {e}")
        
        print(f"🎉 匯入完成！成功匯入 {imported_count} 筆資料")
        
        # 驗證匯入結果
        count = await conn.fetchval("SELECT COUNT(*) FROM documents WHERE import_source = 'excel_import'")
        print(f"📊 資料庫中現有 {count} 筆來自 Excel 的文件")
        
        # 顯示科目統計
        subjects = await conn.fetch("SELECT subject, COUNT(*) as count FROM documents WHERE import_source = 'excel_import' GROUP BY subject")
        print("📈 科目統計:")
        for subject_row in subjects:
            print(f"  {subject_row['subject']}: {subject_row['count']} 筆")
            
    except Exception as e:
        print(f"❌ 匯入過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await conn.close()
        print("📋 資料庫連接已關閉")

async def main():
    print("🚀 開始 Excel 資料匯入程序")
    print("=" * 50)
    await import_excel_to_db()
    print("=" * 50)
    print("✨ 程序執行完畢")

if __name__ == "__main__":
    asyncio.run(main())