#!/usr/bin/env python3
"""
為Template表新增question_type欄位的資料庫遷移腳本
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def add_question_type_column():
    """為templates表新增question_type欄位"""
    try:
        # 建立連線
        db_url = os.getenv('DATABASE_URL', 'postgresql://edurag_user:edurag_password@localhost:5432/edurag')
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        print("連接到資料庫...")
        conn = await asyncpg.connect(db_url)
        
        # 檢查欄位是否已存在
        print("檢查question_type欄位是否存在...")
        exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'templates' 
                AND column_name = 'question_type'
            )
        """)
        
        if exists:
            print("✅ question_type欄位已存在，跳過建立")
        else:
            print("新增question_type欄位到templates表...")
            await conn.execute("""
                ALTER TABLE templates 
                ADD COLUMN question_type VARCHAR(32) DEFAULT 'single_choice'
            """)
            print("✅ 成功新增question_type欄位")
        
        # 更新現有模板的question_type（根據模板名稱推測）
        print("更新現有模板的question_type...")
        
        # 更新是非題模板
        await conn.execute("""
            UPDATE templates 
            SET question_type = 'true_false' 
            WHERE (name LIKE '%是非%' OR name LIKE '%True/False%' OR name LIKE '%true/false%')
            AND question_type = 'single_choice'
        """)
        
        # 更新配對題模板
        await conn.execute("""
            UPDATE templates 
            SET question_type = 'matching' 
            WHERE (name LIKE '%配對%' OR name LIKE '%Matching%' OR name LIKE '%matching%')
            AND question_type = 'single_choice'
        """)
        
        # 更新填空題模板
        await conn.execute("""
            UPDATE templates 
            SET question_type = 'cloze' 
            WHERE (name LIKE '%填空%' OR name LIKE '%Fill%' OR name LIKE '%blank%')
            AND question_type = 'single_choice'
        """)
        
        # 更新簡答題模板
        await conn.execute("""
            UPDATE templates 
            SET question_type = 'short_answer' 
            WHERE (name LIKE '%簡答%' OR name LIKE '%Short Answer%' OR name LIKE '%short_answer%')
            AND question_type = 'single_choice'
        """)
        
        print("✅ 已更新現有模板的題型")
        
        # 顯示更新後的統計
        stats = await conn.fetch("""
            SELECT question_type, COUNT(*) as count 
            FROM templates 
            GROUP BY question_type 
            ORDER BY count DESC
        """)
        
        print("\n📊 模板題型統計：")
        for row in stats:
            print(f"  {row['question_type']}: {row['count']} 個模板")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 遷移失敗: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(add_question_type_column())
    if success:
        print("\n🎉 資料庫遷移完成！Templates表已新增question_type欄位")
    else:
        print("\n❌ 資料庫遷移失敗")