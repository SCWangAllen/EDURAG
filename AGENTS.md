# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

> 本文件於 2026-07-03 依全 repo 實地考古整份重寫,為理解專案與進行任何改動的權威依據。
> 結論均附來源路徑;標「(推測)」者為未經直接證據確認的判斷。


## Project Overview

EduRAG 是 RAG 教育出題系統:教師上傳課程教材(國小 G1–G6,健康/英文/歷史等科目),
後端切塊、向量化存入 pgvector,依科目/題型/數量透過 Claude API 生成 10 種題型的題目,
最後組卷匯出 PDF/Markdown。

**Language**: 以繁體中文回答為主(必要時附英文關鍵詞)。

**LLM Provider**: **Anthropic(唯一)**。程式直接使用 `anthropic.AsyncAnthropic`
(`backend/app/core/llm_client.py:25-27`),model 由 `LLM_MODEL_NAME` 決定
(預設 `claude-sonnet-4-20250514`),tenacity 重試 3 次。
`requirements.txt` 中的 langchain 為零 import 死依賴,**勿使用、勿擴大**。
`.env.example`、`docker-compose.prod.yml`(`LLM_PROVIDER:-openai`)與
`.claude/steering/tech.md` 仍殘留 OpenAI/LangChain 敘述,皆屬過時,以本文件為準。

**⚠️ Embedding 現況為 placeholder**:真實模式回傳 MD5 hash 衍生的 1536 維假向量,
mock 模式回傳全零向量(`backend/app/core/embeddings.py:7-21`)。專案內無任何真實
embedding 模型;RAG 的語意檢索品質尚未真正落地。


## Development Commands

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Mock mode(不需 DB/LLM)
USE_MOCK_API=true uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Tests(全走 mock 模式,不需 DB)
pytest tests/ -v
pytest tests/test_health.py -v
pytest tests/ -v --cov=app

# Lint & format(line-length 88,設定在 backend/pyproject.toml)
ruff check app/
black app/
```

### Frontend
```bash
cd frontend
npm install
npm run dev       # Vite dev server, port 5173(vite.config.js)
npm run build     # production build —— 前端唯一的驗證守門
npm run preview
```
前端**無 lint、無 test script**;`npm run build` 成功是唯一機械式檢查。

### Docker(5 個 compose 檔,注意疊加行為)
| 檔案 | 用途 | Ports(host) |
|---|---|---|
| `docker-compose.yml` + `docker-compose.override.yml` | 預設開發 stack;**override 會自動疊加**(掛 `backend/migrations`、開 postgres 全量 log) | backend 8988、frontend 8989、postgres 5435、pgadmin 5055 |
| `docker-compose.dev.yml` | 獨立隔離環境 `edurag-dev`(Vite HMR) | 3001 / 8987 / 5436 / 5056 |
| `docker-compose.prod.yml` | 生產(nginx 80/443、backend 2 workers、healthcheck);⚠️ 引用的 `./nginx.prod.conf` 與 `./ssl` **不在 repo 中** | frontend 3000、postgres 5432 |
| `docker-compose.v2.yml` | 遺留(已 gitignore),**勿用** | — |

```bash
docker-compose up -d                              # = yml + override
docker-compose -f docker-compose.prod.yml up -d   # production
```

### Database
```bash
./scripts/db-init.sh init     # 灌 backend/db/init.sql(透過 docker exec edurag_postgres)
./scripts/db-init.sh reset    # 需 y 確認;down + 刪 volume + 重灌
./scripts/db-init.sh check    # pg_isready + check_database_health()
# 另有 backup / restore 子指令

cd backend
alembic upgrade head                               # 套用 migrations(唯一機制,見下)
alembic revision --autogenerate -m "description"   # 產生新 migration
```

**Migration 機制:Alembic 是唯一機制。** schema 變更一律走 `alembic revision`;
`backend/migrations/*.sql`(手寫 SQL + `run-migrations.sh`)凍結為歷史紀錄,**不再新增**。
已知遺留:真實模式啟動時 `main.py:22-23` 仍會 `Base.metadata.create_all` 補表,
這是隱式建表行為,不要依賴它做 schema 演進。


## Spec-First Workflow(必遵循)

動工前依序:
1. **Requirements** — `specs/requirements.md`(user stories、驗收條件)
2. **Design** — `specs/design.md`(架構、模組邊界、取捨)
3. **Tasks** — `specs/tasks.md` 拆解任務
4. **Execute** — 前三步確認後才產碼

另讀 `.claude/steering/*.md`(product / tech / structure)。
注意:`specs/` 整個目錄被 `.gitignore` 忽略(未入版控);steering/tech.md 的
LLM 堆疊敘述已過時(見 Project Overview)。


## Architecture

### Backend(FastAPI + SQLAlchemy async + PostgreSQL/pgvector)

```
backend/app/
├── main.py              # FastAPI(debug=True)、CORS、mock/real 雙軌 router 註冊、create_all
├── core/
│   ├── config.py        # 全部環境變數(見文末清單);缺 DATABASE_URL/ANTHROPIC_API_KEY 即 raise
│   ├── llm_client.py    # AsyncAnthropic、max_tokens=16384、temperature=0.7、題型 _TYPE_HINTS
│   └── embeddings.py    # ⚠️ MD5 假向量 placeholder(1536 維)
├── routers/             # 11 個真實 router + 5 個 mock router
├── services/            # 9 個 service class,建構子注入 AsyncSession,全 async
├── schemas/             # Pydantic(v1/v2 風格混用;ORM 用 Config.from_attributes)
├── db/
│   ├── database.py      # create_async_engine + AsyncSession;mock 模式 get_db 回 503
│   ├── models.py        # 6 個 model —— schema 權威(見 Database 節)
│   └── init.sql         # v2.1.0 初始化快照(已與 models.py 漂移,見 Database 節)
├── alembic/             # migrations(001_add_image_questions、002_subject_grade_decouple)
└── prompts/             # 僅 matching.txt、true_false.txt;其他題型靠 llm_client 內嵌 hints
```

**Router prefix 對照**(main.py:26-53):
- `/api` 前綴:`generate`、`questions`、`documents`、`subjects`、`ingest`、`upload`、
  `dashboard`、`image-questions`、`images`
- **例外(歷史遺留,勿仿效)**:`templates` → `/templates`(templates.py:16)、`health` → `/health`
- 代表 endpoints:generate 有 `/`、`/batch`、`/template`、`/template/batch`、`/prompt`、
  `/template-enhanced`;questions 有 CRUD + `/stats`、`/batch-delete`、`/export`;
  upload 有 `/excel`、`/template`;templates 有 CRUD + `/subjects`、`/initialize-defaults`

**Mock mode**:`USE_MOCK_API=true` 時 main.py 改註冊 mock router。
**Mock 變體只有 5 個**(ingest/generate/questions/templates/dashboard);
documents/upload/subjects/image_questions/images 無 mock 版。
注意 `mock_questions` 的 prefix 是 `/api/mock/questions`,與真實版不同。
Mock 回應 schema 必須與真實 API 一致。

### Frontend(Vue 3 Composition API + Vite + Tailwind)

```
frontend/src/
├── router/index.js      # 8 條 route:/ 是 redirect → /exam-paper;其餘 7 頁:
│                        #   /dashboard /templates /documents /questions /generate
│                        #   /exam-paper /image-questions(全部懶載入)
├── views/               # 7 個頁面,檔名 PascalCase
├── components/          # 53 檔,檔名與子目錄全 PascalCase
│                        #   (Documents/ ExamDesigner/ ExamPaper/ ExamPreview/ Generate/
│                        #    ImageQuestions/ Questions/ Templates/;ExamPaper/ 最大有 12 檔)
├── api/                 # 一資源一檔;axios.js 無 interceptor
│                        #   ⚠️ templateService.js 打 /templates(無 /api 前綴),與後端耦合
├── composables/         # useLanguage(已硬鎖 'zh',切換停用)、useToast、useLocalStorage
├── i18n/languages.js    # zh/en 翻譯(實際只用 zh)
└── utils/               # eventBus(mitt 包成 EventBus class + eventTypes.js)、
                         # pdfExporter(動態 import jspdf)、
                         # markdownExporter(無第三方庫,手工組字串 + Blob 下載)
```

- **狀態管理**:無 Pinia/Vuex;composables + localStorage(5 檔 17 處)+ mitt event bus。
- **API base URL**(`api/axios.js:7-21`):`VITE_API_BASE_URL` → 非 localhost 時
  `http://<hostname>:8988` → fallback `http://localhost:8988`。
- **錯誤呈現**:API 錯誤經 event bus → 全域 `Toast.vue`;訊息取用順序
  `error.response.data.detail → error.message → 預設`(Toast.vue:78)。

### 目錄中的非主線內容(勿動、勿混淆)
- `edurag-vue/`(repo root):殘留的 Vite 快取空殼(只有 `.vite/`),非新版前端、
  非 submodule,可安全刪除。真正前端在 `frontend/`(其 package name 恰為 `edurag-vue`)。
- `frontend/agent-service-toolkit/`:vendored 第三方 LangGraph repo,未被 git 追蹤,
  與本專案主線無關。
- `Questions/`(教材 .docx + 圖檔)與 `data/`(執行期圖片,掛入 backend 容器):皆 gitignored。
- `backend/db/init_from_current_db.sql`(標 v3.0.0):2025-09-28 生產庫 dump 快照,
  未被任何腳本使用,**不要以它為基底改 schema**(推測為歷史快照)。
- `backend/db/README.md` 過時(自稱 v2.0.0、提及不存在的 init_complete.sql)。

### Key Data Flow
1. **Ingest**:上傳文件 → 切塊 → 產生 embedding(現為假向量)→ 存 pgvector
2. **Generate**:參數(科目/題型/數量)→ cosine 相似度取回 chunks(TOP_K=8、閾值 0.1)
   → 組 prompt → Claude API → 解析結構化題目 → 存 DB
3. **Export**:選題 → 組卷 → 匯出 PDF(jspdf)/ Markdown(手工字串)


## Database(PostgreSQL 15 + pgvector)

**Schema 權威:`backend/app/db/models.py` + Alembic migrations。**
`db/init.sql`(v2.1.0)僅為初始化快照,已知與 models.py 漂移;改 schema 後應回寫同步。

6 張表(models.py;init.sql 只有前 5 張):

| 表 | 重點 | 關聯 / 索引 |
|---|---|---|
| `subjects` | name、color、grade、is_active;**UniqueConstraint(name, grade)**(models.py:205-213) | ← templates.subject_id(無 cascade) |
| `documents` | subject、content、image_urls TEXT[]、image_data(base64)、grade | ← embeddings(**ON DELETE CASCADE**)、← questions(無 cascade) |
| `templates` | content、question_type、params JSONB、grades JSON | ← questions.template_id(無 cascade) |
| `embeddings` | slice_text、`vector VECTOR(1536)` | **IVFFlat** `vector_cosine_ops`(init.sql:84,未設 lists) |
| `questions` | question_type、stem、options TEXT[]、answer、question_data JSONB、source_metadata JSONB、export_batch_id | **GIN** ×2(question_data、source_metadata) |
| `image_questions` | 僅在 models.py:237 + Alembic 001;**init.sql 尚無** | — |

另有:`schema_version` 表、相容視圖 `document_chunks` / `generated_questions`、
`update_updated_at_column()` trigger(掛 4 表)、`check_database_health()` 函數、
seed 資料(6 科目 / 3 模板 / 3 範例文件)。

**已知漂移(init.sql 落後於 models.py)**:缺 `image_questions` 表、缺 `templates.grades`、
subjects 仍是 `name UNIQUE`(而非複合 unique)、grade 欄位長度不一。

**`questions.question_data` JSONB 依題型結構化**(schemas/question.py:25-43、
llm_client.py:182-207):matching=`{left_items, right_items}`、sequence=`{items}`、
enumeration=`{category, min_items, max_items}`、
symbol_identification=`{symbol_description, symbol_context}`。
前端 `ExamPreview/QuestionRenderer.vue` 依此結構渲染 —— 後端改格式必須同步前端。

無 Redis、無快取層、無第二資料庫。

### Question Types(QuestionType enum,schemas/question.py:5-17)
`single_choice`, `cloze`, `short_answer`, `true_false`, `matching`, `sequence`,
`enumeration`, `symbol_identification`, `mixed`, `auto`


## Conventions

- **Python**:snake_case;ruff(E/W/F/I/B/C4/UP)+ black,line-length 88(backend/pyproject.toml);
  全面 async;Pydantic 為所有 request/response 建模(現存 v1/v2 validator 混用,新碼用 v2 `field_validator`)
- **Frontend**:**檔名一律 PascalCase**(views、components、子目錄皆然);變數 camelCase;
  新路由懶載入;狀態走 composables/localStorage/event bus(不引入 Pinia);UI 文案進 `i18n/languages.js`
- **API style**:RESTful、名詞複數;新 endpoint 一律掛 `/api` 前綴
  (`/templates`、`/health` 是既有例外,勿仿效)
- **錯誤處理**:現況為各 router 散用 `raise HTTPException(status_code, detail=...)`,
  無統一錯誤碼結構、無全域 exception handler。
  **目標(尚未實作)**:統一錯誤碼格式。新碼朝目標靠攏,但回應必須保留 `detail` 欄位
  (前端 Toast 依賴它)。
- **新 API route 必附**:router、Pydantic schema、最小測試;若該資源已有 mock 版,
  mock router 需同步更新且 schema 與真實版一致
- **測試**:pytest + pytest-asyncio + httpx;現有 3 檔(test_health / test_mock_apis /
  test_templates)全走 mock 模式、不需 DB;無前端測試、**無 CI** —— 本機驗證是唯一防線
- **Git**:Conventional Commits(`feat:` 等);remote origin=SCWangAllen/EDURAG、
  upstream=shric-abraham/AbrahamExamAI;現用分支 `clean-main`


## 改動原則(動手前必讀)

### 高風險區
- **Schema 變更**:一律走 Alembic revision,並回寫 `init.sql` 保持快照同步;
  歷史上三軌並行(init.sql / migrations/*.sql / Alembic)造成的漂移尚未清完,改表前先比對
- **`core/embeddings.py`**:換真實 embedding 模型時,既有向量資料全部失效需重建;
  維度非 1536 還要動 schema + IVFFlat index
- **`/templates` prefix**:後端改 `/api/templates` 會同時破壞 `frontend/src/api/templateService.js`,必須同步
- **Port / baseURL**:8988 寫死在 axios.js fallback;改 port 要同時查 compose 與 axios.js
- **`docker-compose.override.yml` 自動疊加**:debug 環境問題時記得它存在
- **`question_data` JSONB**:前後端耦合(QuestionRenderer)
- **認證/授權:不存在**,所有 API 無 auth —— 涉及對外部署的功能一律視為高風險改動

### 驗證要求(改完才算完成)
- 後端:`pytest tests/ -v` + `ruff check app/` + `black --check app/`
- 前端:`npm run build` 成功
- 涉及 DB:`./scripts/db-init.sh check`;涉及整合:`docker-compose up -d` 後打 `GET /health`

### 禁止事項
- 不寫任何 LangChain 用法;不引入 OpenAI 相關設定
- 不參考 `.env.example` 的 port/LLM 設定(過時);不用 `docker-compose.v2.yml`;
  不以 `init_from_current_db.sql` 為基底改 schema;不再新增 `backend/migrations/*.sql`
- 不動 `frontend/agent-service-toolkit/` 與 `edurag-vue/`
- 不 commit `.env`、`data/`、`Questions/`
- 不依賴 `create_all` 做 schema 演進


## Environment Variables

後端(`backend/app/core/config.py:7-46`;缺前兩項即啟動失敗):
- `DATABASE_URL` — PostgreSQL async 連線字串(`postgresql+asyncpg://...`)
- `ANTHROPIC_API_KEY` — Claude API key
- `USE_MOCK_API` — `true` 啟用 mock 模式(不需 DB/LLM)
- `LLM_MODEL_NAME` — 預設 `claude-sonnet-4-20250514`
- `CORS_ORIGINS`、`IMAGES_BASE_DIR`
- RAG 調參:`RETRIEVAL_TOP_K`(8)、`SIMILARITY_THRESHOLD`(0.1)、
  `DEFAULT_CHUNK_SIZE`(300)、`CHUNK_OVERLAP`(50)、`UPLOAD_CHUNK_SIZE`(500)

前端:`VITE_API_BASE_URL`(覆寫 API base URL)、`VITE_API_URL`(vite dev proxy 目標)。

⚠️ 根目錄 `.env.example` 嚴重過時(舊 port、OPENAI_API_KEY),不要照抄;
以 `config.py` 與 `docker-compose.yml` 為準。
