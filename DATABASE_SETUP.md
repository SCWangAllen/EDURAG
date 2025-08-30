# EduRAG 資料庫設定指南

本專案現已支援完整的 PostgreSQL 資料庫環境，包含模版管理、文件管理等功能。

## 快速開始

### 1. 啟動資料庫服務

在專案根目錄執行：

```bash
# 啟動 PostgreSQL 和 pgAdmin
docker-compose up -d

# 查看服務狀態
docker-compose ps
```

### 2. 訪問服務

- **PostgreSQL**: localhost:5432
  - 資料庫: `edurag`
  - 用戶: `edurag_user`
  - 密碼: `edurag_password`

- **pgAdmin**: http://localhost:5050
  - 登入: admin@edurag.com
  - 密碼: admin123

### 3. 啟動後端 API

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 啟動前端

```bash
cd frontend
npm install
npm run dev
```

## 資料庫結構

### 主要表格：

1. **templates** - 題目生成模版
   - 支援健康、英文、歷史三個科目
   - 包含 Prompt 模版和 LLM 參數設定
   
2. **documents** - 教材文件
   - 支援章節分類和科目標籤
   - 支援圖片與文字關聯
   
3. **document_chunks** - 文件向量化片段
   - 使用 pgvector 儲存 1536 維度向量
   - 支援語義搜尋和相關性檢索
   
4. **generated_questions** - 生成的題目記錄
   - 儲存歷史生成記錄
   - 支援批次匯出功能

## 功能特色

### ✅ 已完成功能：

1. **多語言支援** - 完整的中英文界面切換
2. **模版管理** - CRUD 操作，支援版本控制
3. **科目管理** - 健康、英文、歷史三科預設模版
4. **資料庫存儲** - PostgreSQL + pgvector 向量資料庫
5. **語言響應式** - 切換語言時自動更新模版內容

### 🚧 開發中功能：

1. **文件管理** - Excel 批量匯入、章節管理
2. **向量搜尋** - 文件語義檢索
3. **批次匯出** - 題目批次匯出功能
4. **圖片處理** - 圖文關聯與 OCR

## 配置說明

### 環境變數 (.env)

```bash
# API 模式 (false = 使用真實資料庫)
USE_MOCK_API=false

# 資料庫配置
DATABASE_URL=postgresql+asyncpg://edurag_user:edurag_password@localhost:5432/edurag

# OpenAI API (用於 LLM 題目生成)
OPENAI_API_KEY=your-openai-api-key-here

# 向量維度
VECTOR_DIMENSION=1536
```

## 常用操作

### 初始化預設模版

訪問 Templates 頁面，點擊「初始化預設模版」按鈕，系統會自動建立：

- **健康單選題模版** - 健康教育相關題目
- **英文單選題模版** - 英語學習相關題目  
- **歷史單選題模版** - 歷史知識相關題目

### 資料庫管理

使用 pgAdmin (http://localhost:5050) 進行：

- 查看表格結構和數據
- 執行 SQL 查詢
- 監控資料庫效能
- 備份與還原資料

### 停止服務

```bash
# 停止所有服務
docker-compose down

# 停止並移除資料卷 (⚠️ 會刪除所有資料)
docker-compose down -v
```

## 疑難排解

### 資料庫連接問題

1. 確認 Docker 服務正常運行：`docker-compose ps`
2. 檢查 .env 檔案配置
3. 查看資料庫日誌：`docker-compose logs postgres`

### 模版不顯示問題

1. 確認 `USE_MOCK_API=false` 
2. 執行模版初始化功能
3. 檢查資料庫中是否有資料：`SELECT * FROM templates;`

### 語言切換無效

1. 清除瀏覽器快取
2. 確認 localStorage 中的 language 設定
3. 重新載入頁面

## 開發注意事項

- 模版內容使用 `{context}` 作為文章內容替換標記
- 向量搜尋需要 OpenAI API Key 進行 embedding
- 資料庫變更需要建立 migration scripts
- 測試時可切換 `USE_MOCK_API=true` 使用 Mock 資料