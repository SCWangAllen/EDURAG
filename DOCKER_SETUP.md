# EduRAG Docker 部署指南

## 快速開始

### 1. 環境準備
確保系統已安裝：
- Docker (20.10+)
- Docker Compose (2.0+)

### 2. 設定環境變數
```bash
# 複製環境變數範例檔
cp .env.example .env

# 編輯 .env 檔案，設定必要的參數
# 特別注意要設定 OPENAI_API_KEY
nano .env
```

### 3. 啟動服務

#### 一鍵啟動所有服務
```bash
docker-compose up -d
```

#### 或分別建置和啟動
```bash
# 建置映像檔
docker-compose build

# 啟動服務
docker-compose up -d
```

### 4. 服務訪問

服務啟動後，可以通過以下地址訪問：

- **前端應用**: http://localhost:3000
- **後端 API**: http://localhost:8000
- **API 文檔**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050
  - 預設帳號：admin@edurag.com (或您在 .env 中設定的值)
  - 預設密碼：admin123 (或您在 .env 中設定的值)

## 常用指令

### 查看服務狀態
```bash
docker-compose ps
```

### 查看服務日誌
```bash
# 查看所有服務日誌
docker-compose logs

# 查看特定服務日誌
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# 即時追蹤日誌
docker-compose logs -f backend
```

### 停止服務
```bash
# 停止所有服務
docker-compose stop

# 停止並移除容器
docker-compose down

# 停止並移除容器、volumes（會刪除資料）
docker-compose down -v
```

### 重新建置服務
```bash
# 重新建置並啟動
docker-compose up -d --build

# 只重新建置特定服務
docker-compose up -d --build backend
```

## 開發模式

### 熱重載開發
當前配置已支援熱重載：
- Backend: 檔案變更會自動重啟服務
- Frontend: 支援 HMR (Hot Module Replacement)

### 進入容器除錯
```bash
# 進入 backend 容器
docker-compose exec backend bash

# 進入 postgres 容器
docker-compose exec postgres psql -U edurag_user -d edurag
```

## 資料庫管理

### 使用 pgAdmin
1. 訪問 http://localhost:5050
2. 使用 .env 中設定的帳號密碼登入
3. 伺服器已預先配置，直接連接即可

### 資料庫備份
```bash
# 備份資料庫
docker-compose exec postgres pg_dump -U edurag_user edurag > backup.sql

# 還原資料庫
docker-compose exec -T postgres psql -U edurag_user edurag < backup.sql
```

## 故障排除

### 1. 端口衝突
如果端口已被佔用，可在 .env 中修改對應的端口設定：
```env
FRONTEND_PORT=3001
BACKEND_PORT=8001
PGADMIN_PORT=5051
```

### 2. 資料庫連接失敗
確保 DATABASE_URL 正確設定，Docker 環境中應使用：
```env
DATABASE_URL=postgresql+asyncpg://edurag_user:your_password@postgres:5432/edurag
```

### 3. 前端無法連接後端
檢查 nginx.conf 中的 proxy_pass 設定是否正確指向 backend 服務。

### 4. 清理所有 Docker 資源
```bash
# 停止並清理所有容器、網路、volumes
docker-compose down -v --remove-orphans

# 清理未使用的映像檔
docker image prune -a
```

## 生產環境部署建議

1. **環境變數安全**：
   - 使用 Docker Secrets 或環境變數管理工具
   - 不要將 .env 檔案提交到版本控制

2. **資料持久化**：
   - 確保 volumes 正確配置
   - 定期備份資料庫

3. **性能優化**：
   - 調整 PostgreSQL 配置參數
   - 使用 Redis 作為快取層（如需要）

4. **監控與日誌**：
   - 整合 Prometheus + Grafana 監控
   - 使用 ELK Stack 進行日誌管理

## 專案結構

```
EduRAG/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── src/
├── docker/
│   └── pgadmin/
│       └── servers.json
├── docker-compose.yml
├── .env.example
└── .env (需自行建立)
```