# EduRAG 資料庫設定文件

## 📊 資料表結構

### 1. **subjects** - 科目表
- 管理所有科目資訊
- 與模板建立關聯

### 2. **documents** - 文件表
- 儲存教材內容
- 支援圖片、章節、頁碼等元資料

### 3. **templates** - 模板表
- 題目生成模板
- 支援不同題型和參數設定
- 關聯到科目

### 4. **embeddings** - 向量嵌入表
- 儲存文件的向量表示
- 用於 RAG 檢索

### 5. **questions** - 題目表
- 儲存生成的題目
- 支援多種題型（單選、多選、配對等）
- 包含題幹、選項、答案、解釋

## 🚀 快速開始

### 方法一：使用管理腳本（推薦）

```bash
# 賦予執行權限
chmod +x scripts/db-init.sh

# 初始化資料庫
./scripts/db-init.sh init

# 檢查狀態
./scripts/db-init.sh check

# 完全重置（刪除所有資料）
./scripts/db-init.sh reset
```

### 方法二：使用 Docker Compose

```bash
# 啟動服務（自動初始化）
docker-compose up -d

# 查看初始化日誌
docker-compose logs postgres

# 驗證初始化
docker exec edurag_postgres psql -U edurag_user -d edurag -c "\dt"
```

### 方法三：手動初始化

```bash
# 進入 PostgreSQL 容器
docker exec -it edurag_postgres bash

# 執行初始化腳本
psql -U edurag_user -d edurag -f /docker-entrypoint-initdb.d/01-init.sql
```

## 📁 檔案說明

- **init.sql**: 原始的基本初始化腳本
- **init_complete.sql**: 完整的資料庫結構（推薦使用）
- **README.md**: 本文件

## 🔄 資料庫版本管理

目前版本：**2.0.0**

查看版本：
```sql
SELECT * FROM schema_version;
```

## 🛠️ 資料庫操作

### 備份資料庫
```bash
./scripts/db-init.sh backup
```

### 還原資料庫
```bash
./scripts/db-init.sh restore backup/edurag_backup_20250928_120000.sql
```

### 連接資料庫
```bash
# 使用 psql
docker exec -it edurag_postgres psql -U edurag_user -d edurag

# 使用 pgAdmin
# 開啟瀏覽器訪問 http://localhost:5050
# 帳號：admin@edurag.com
# 密碼：（查看 .env 檔案中的 PGADMIN_PASSWORD）
```

## 📝 常用 SQL 查詢

### 查看所有表
```sql
\dt
```

### 查看表結構
```sql
\d+ questions
```

### 查看資料統計
```sql
SELECT * FROM check_database_health();
```

### 查看各科目的模板數
```sql
SELECT s.name, COUNT(t.id) as template_count
FROM subjects s
LEFT JOIN templates t ON s.id = t.subject_id
GROUP BY s.id, s.name
ORDER BY s.name;
```

### 查看最近生成的題目
```sql
SELECT q.id, q.question_type, q.stem, d.title as source_document
FROM questions q
LEFT JOIN documents d ON q.document_id = d.id
ORDER BY q.created_at DESC
LIMIT 10;
```

## ⚠️ 注意事項

1. **初次使用**：確保 `.env` 檔案已正確設定
2. **pgvector 擴充套件**：需要使用 `pgvector/pgvector:pg15` 映像
3. **資料一致性**：使用 `init_complete.sql` 確保與 `models.py` 同步
4. **權限問題**：確保 `edurag_user` 有適當的資料庫權限

## 🐛 疑難排解

### 問題：擴充套件安裝失敗
```sql
-- 手動安裝 pgvector
CREATE EXTENSION IF NOT EXISTS vector;
```

### 問題：外鍵約束錯誤
```sql
-- 檢查關聯
SELECT * FROM subjects;
SELECT * FROM templates WHERE subject_id IS NOT NULL;
```

### 問題：初始化腳本執行失敗
```bash
# 清理並重新開始
docker-compose down -v
docker-compose up -d
```

## 📚 相關文件

- [PostgreSQL 官方文件](https://www.postgresql.org/docs/)
- [pgvector 文件](https://github.com/pgvector/pgvector)
- [SQLAlchemy 文件](https://docs.sqlalchemy.org/)