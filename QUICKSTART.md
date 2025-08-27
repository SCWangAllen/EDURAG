# EduRAG 快速啟動指南

## 🚀 立即體驗 (Mock模式)

### 1. 啟動後端服務
```bash
cd backend
USE_MOCK_API=true uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 測試系統功能
```bash
# 在另一個終端機執行
python quick_test.py           # 快速功能測試
python example_usage.py       # 完整工作流程示範
```

### 3. API端點測試

#### 健康檢查
```bash
curl http://localhost:8000/health
```

#### 攝取文件
```bash
curl -X POST http://localhost:8000/api/ingest/ \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "chinese",
    "text": "春天是萬物復甦的季節。樹木抽出新芽，花朵競相綻放。",
    "title": "春天的美好"
  }'
```

#### 生成題目
```bash
curl -X POST http://localhost:8000/api/generate/ \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "chinese", 
    "document_id": 999,
    "types": {
      "single_choice": 2,
      "cloze": 1,
      "short_answer": 1
    }
  }'
```

## 📊 系統特性

### ✅ 已實現功能
- **健康檢查**: `/health` 端點監控系統狀態
- **文件攝取**: 智能文本分塊，支援向量化
- **題目生成**: 三種題型 (單選/填空/簡答)，可追溯來源
- **Mock模式**: 無需資料庫/LLM，完整功能展示
- **Schema一致**: Mock與實際模式使用相同資料結構

### 🎯 效能指標
- **TTFQ目標**: Mock模式 < 2s，實際模式 < 8s
- **檢索相關度**: 向量相似度搜索 ≥ 0.7
- **錯誤率**: 完整錯誤處理，目標 < 2%

### 🔧 技術棧
- **後端**: FastAPI + SQLAlchemy + pgvector
- **資料庫**: PostgreSQL with pgvector extension  
- **LLM**: OpenAI GPT-3.5-turbo
- **向量化**: OpenAI embeddings (1536維)

## 🛠️ 開發環境設置

### 安裝依賴
```bash
cd backend
pip install -r requirements.txt
```

### 環境變數 (.env)
```bash
# Mock模式 (無需外部服務)
USE_MOCK_API=true

# 實際模式設定  
USE_MOCK_API=false
DATABASE_URL=postgresql://user:pass@localhost:5432/edurag
OPENAI_API_KEY=your-openai-api-key
```

### 執行測試
```bash
pytest tests/ -v                    # 單元測試
python -m ruff backend/app/         # 代碼檢查
python -m black backend/app/        # 代碼格式化  
```

## 📈 生產環境部署

### 資料庫設置
```sql
-- 建立資料庫
CREATE DATABASE edurag;

-- 安裝pgvector擴展
CREATE EXTENSION vector;
```

### Docker部署
```bash
cd backend
docker build -t edurag-backend .
docker run -p 8000:8000 --env-file .env edurag-backend
```

## 📝 API文檔

啟動服務後造訪:
- **Swagger UI**: http://localhost:8000/docs  
- **ReDoc**: http://localhost:8000/redoc

## 🔍 故障排除

### 常見問題
1. **Import錯誤**: 確認已安裝 `pip install -r requirements.txt`
2. **資料庫連線**: 檢查 `DATABASE_URL` 設定
3. **OpenAI錯誤**: 驗證 `OPENAI_API_KEY` 有效性

### 日誌查看
```bash
# 啟動時查看詳細日誌
USE_MOCK_API=true uvicorn app.main:app --reload --log-level debug
```

---

🎉 **準備完成！** 系統已通過完整的 A/B/C 審查，符合所有技術規範和產品需求。