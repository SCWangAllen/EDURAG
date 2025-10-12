# EduRAG 專案完整架構文件

> **版本**: 2.0.0
> **最後更新**: 2025-10-11
> **文件狀態**: Complete

---

## 📋 目錄

1. [專案概覽](#1-專案概覽)
2. [系統架構](#2-系統架構)
3. [後端架構](#3-後端架構)
4. [前端架構](#4-前端架構)
5. [資料庫設計](#5-資料庫設計)
6. [部署架構](#6-部署架構)
7. [開發規範](#7-開發規範)
8. [技術決策](#8-技術決策)

---

## 1. 專案概覽

### 1.1 產品定位

**EduRAG** 是一個基於 RAG（Retrieval-Augmented Generation）技術的**教育題目生成系統**，專為教育場景打造，讓教師與助教能夠：

- 📚 快速上傳教材並生成多樣化題目
- 🔍 追溯每道題目的來源段落
- ⚙️ 控制題目生成參數與品質
- 📊 管理模板、科目、文件與題庫

### 1.2 核心技術棧

```mermaid
graph LR
    A[前端] -->|Vue 3 + Vite| B[Tailwind CSS]
    C[後端] -->|FastAPI + Python 3.11| D[LangChain]
    E[資料庫] -->|PostgreSQL 15| F[pgvector]
    G[LLM] -->|Anthropic Claude| H[Sonnet 3.5]

    style A fill:#42b883
    style C fill:#009688
    style E fill:#336791
    style G fill:#FF6B6B
```

| 層級 | 技術選型 | 版本 |
|------|---------|------|
| **前端** | Vue 3 (Composition API) | 3.5.17 |
| **構建工具** | Vite | 7.0.4 |
| **樣式** | Tailwind CSS | 3.4.17 |
| **後端** | FastAPI | 0.111.0 |
| **語言** | Python | 3.11+ |
| **資料庫** | PostgreSQL + pgvector | 15 |
| **ORM** | SQLAlchemy (async) | 2.0.19 |
| **向量搜尋** | pgvector | - |
| **LLM** | Anthropic Claude | Sonnet 3.5 |
| **RAG 框架** | LangChain | 0.2.3 |

### 1.3 核心功能

```mermaid
mindmap
  root((EduRAG))
    文件管理
      手動上傳
      Excel 批量匯入
      章節管理
      圖片儲存
    題目生成
      基礎題型
        單選題
        填空題
        簡答題
      擴展題型
        是非題
        配對題
        排序題
        列舉題
        符號識別題
      生成模式
        基礎生成
        模板驅動
        批次生成
        Prompt 生成
    模板系統
      模板 CRUD
      參數配置
      版本管理
      科目分類
    題庫管理
      題目 CRUD
      批量操作
      匯出功能
      考券設計
```

---

## 2. 系統架構

### 2.1 整體架構圖

```mermaid
graph TB
    subgraph "使用者層"
        U1[教師]
        U2[助教]
        U3[內容編輯]
    end

    subgraph "前端層 (Vue 3)"
        FE1[Generate 生成頁面]
        FE2[Templates 模板頁面]
        FE3[Documents 文件頁面]
        FE4[Questions 題目頁面]
        FE5[Dashboard 儀表板]
    end

    subgraph "API 層 (FastAPI)"
        API1[/api/generate]
        API2[/api/templates]
        API3[/api/documents]
        API4[/api/questions]
        API5[/api/subjects]
        API6[/api/ingest]
    end

    subgraph "服務層 (Business Logic)"
        SVC1[Generate Service]
        SVC2[Template Service]
        SVC3[Document Service]
        SVC4[Question Service]
        SVC5[Retrieval Service]
        SVC6[Ingest Service]
    end

    subgraph "資料存取層"
        DB1[(PostgreSQL)]
        DB2[(pgvector)]
    end

    subgraph "外部服務"
        LLM1[Claude API]
        LLM2[OpenAI Embeddings]
    end

    U1 & U2 & U3 --> FE1 & FE2 & FE3 & FE4 & FE5
    FE1 --> API1
    FE2 --> API2
    FE3 --> API3 & API6
    FE4 --> API4

    API1 --> SVC1
    API2 --> SVC2
    API3 --> SVC3
    API4 --> SVC4
    API6 --> SVC6

    SVC1 --> SVC5
    SVC1 --> LLM1
    SVC5 --> DB2
    SVC6 --> LLM2

    SVC1 & SVC2 & SVC3 & SVC4 & SVC6 --> DB1

    style FE1 fill:#42b883
    style API1 fill:#009688
    style SVC1 fill:#4CAF50
    style DB1 fill:#336791
    style LLM1 fill:#FF6B6B
```

### 2.2 資料流程圖

#### 2.2.1 文件攝取流程 (Ingest)

```mermaid
sequenceDiagram
    participant U as 使用者
    participant FE as 前端
    participant API as Ingest API
    participant SVC as Ingest Service
    participant EMB as Embeddings Service
    participant DB as PostgreSQL
    participant VEC as pgvector

    U->>FE: 上傳課文
    FE->>API: POST /api/ingest
    API->>SVC: 處理上傳請求

    SVC->>SVC: 文字擷取
    SVC->>SVC: 文本分塊 (300 字/塊)

    loop 每個切片
        SVC->>EMB: 生成向量
        EMB-->>SVC: 1536 維向量
    end

    SVC->>DB: 儲存 Document
    SVC->>VEC: 儲存 Embeddings

    VEC-->>API: 成功
    API-->>FE: IngestResponse
    FE-->>U: 顯示成功
```

#### 2.2.2 題目生成流程 (RAG)

```mermaid
sequenceDiagram
    participant U as 使用者
    participant FE as 前端
    participant API as Generate API
    participant GEN as Generate Service
    participant RET as Retrieval Service
    participant VEC as pgvector
    participant LLM as Claude API
    participant DB as PostgreSQL

    U->>FE: 選擇模板+文件+題數
    FE->>API: POST /api/generate/template-enhanced

    API->>GEN: 解析請求
    GEN->>DB: 查詢模板
    GEN->>DB: 查詢文件

    alt 使用向量檢索
        GEN->>RET: 搜尋相似文本塊
        RET->>VEC: 餘弦相似度搜尋
        VEC-->>RET: Top-K 相關切片
        RET-->>GEN: 相關上下文
    else 使用完整文件
        GEN->>GEN: 組合文件內容
    end

    GEN->>GEN: 組合 Prompt
    note right of GEN: 替換 {context} 佔位符

    GEN->>LLM: 呼叫 Claude API
    note right of LLM: temperature, max_tokens<br/>top_p, frequency_penalty
    LLM-->>GEN: JSON 格式題目

    GEN->>GEN: JSON 解析與驗證
    GEN->>DB: 儲存 Questions

    DB-->>API: 成功
    API-->>FE: GenerateResponse
    FE-->>U: 顯示生成的題目
```

### 2.3 Mock API 模式

```mermaid
graph TD
    A[環境變數 USE_MOCK_API] -->|true| B[Mock 路由]
    A -->|false| C[真實路由]

    B --> D[mock_ingest.py]
    B --> E[mock_generate.py]
    B --> F[mock_templates.py]
    B --> G[mock_questions.py]

    C --> H[ingest.py]
    C --> I[generate.py]
    C --> J[templates.py]
    C --> K[questions.py]

    D & E & F & G --> L[Fixtures 資料]
    H & I & J & K --> M[真實資料庫]

    L --> N[前端 API 呼叫]
    M --> N

    style B fill:#FFA726
    style C fill:#66BB6A
    style N fill:#42A5F5
```

**Mock 模式特性**：
- ✅ **Schema 一致性**：回傳資料與真實 API 完全相同
- ✅ **無依賴**：不需要資料庫、LLM API Key
- ✅ **快速回應**：< 2 秒，適合前端開發
- ✅ **覆蓋範圍**：Ingest、Generate、Templates、Questions、Dashboard

---

## 3. 後端架構

### 3.1 目錄結構

```
backend/
├── app/
│   ├── main.py                    # FastAPI 應用入口
│   │
│   ├── core/                      # 核心設定與工具
│   │   ├── config.py              # 環境變數配置
│   │   ├── embeddings.py          # 向量嵌入服務
│   │   └── llm_client.py          # Claude API 客戶端
│   │
│   ├── db/                        # 資料庫層
│   │   ├── database.py            # AsyncSession、get_db
│   │   └── models.py              # SQLAlchemy 模型
│   │
│   ├── routers/                   # API 路由（控制器層）
│   │   ├── health.py              # 健康檢查
│   │   ├── ingest.py              # 文件上傳與向量化
│   │   ├── generate.py            # 題目生成
│   │   ├── templates.py           # 模板管理
│   │   ├── documents.py           # 文件管理
│   │   ├── questions.py           # 題目管理
│   │   ├── subjects.py            # 科目管理
│   │   ├── dashboard.py           # 統計資訊
│   │   ├── upload.py              # Excel 批次匯入
│   │   └── mock_*.py              # Mock 路由
│   │
│   ├── services/                  # 業務邏輯層
│   │   ├── ingest.py              # 文件擷取與分塊
│   │   ├── generate.py            # 題目生成流程
│   │   ├── retrieval.py           # 向量檢索
│   │   ├── template_service.py    # 模板 CRUD
│   │   ├── document_service.py    # 文件管理
│   │   ├── question_service.py    # 題目管理
│   │   └── subject_service.py     # 科目管理
│   │
│   ├── schemas/                   # Pydantic 資料模型
│   │   ├── ingest.py              # IngestRequest/Response
│   │   ├── question.py            # QuestionType Enum、Generate Schemas
│   │   ├── template.py            # TemplateCreate/Update/Response
│   │   └── subject.py             # SubjectCreate/Update/Response
│   │
│   └── prompts/                   # LLM Prompt 模板
│       ├── matching.txt           # 配對題 Prompt
│       └── true_false.txt         # 是非題 Prompt
│
├── db/                            # 資料庫初始化腳本
│   ├── init.sql                   # 基礎 schema
│   ├── init_complete.sql          # 完整 schema（推薦）
│   └── init_from_current_db.sql   # 生產環境匯出
│
├── tests/                         # 測試
│   ├── test_health.py
│   ├── test_mock_apis.py
│   └── test_templates.py
│
├── migrations/                    # 資料庫遷移
│   └── 001_add_question_data.sql
│
├── requirements.txt               # Python 依賴
└── Dockerfile                     # 容器化
```

### 3.2 API 端點總覽

#### 系統健康檢查

| Method | Path | 功能 | Mock |
|--------|------|------|------|
| GET | `/health` | 健康檢查 | ✅ |

#### 文件管理 (8 個端點)

| Method | Path | 功能 | Mock |
|--------|------|------|------|
| POST | `/api/ingest` | 上傳文件、分塊、向量化 | ✅ |
| GET | `/api/documents/` | 文件清單（分頁、篩選） | ❌ |
| GET | `/api/documents/{id}` | 文件詳情 | ❌ |
| PUT | `/api/documents/{id}` | 更新文件 | ❌ |
| DELETE | `/api/documents/{id}` | 刪除文件 | ❌ |
| GET | `/api/documents/stats` | 文件統計 | ❌ |
| GET | `/api/documents/search` | 文件搜尋 | ❌ |
| POST | `/upload/excel` | Excel 批次匯入 | ❌ |

#### 題目生成 (6 個端點)

| Method | Path | 功能 | Mock |
|--------|------|------|------|
| POST | `/api/generate/` | 基礎生成 | ✅ |
| POST | `/api/generate/batch` | 批次生成 | ✅ |
| POST | `/api/generate/template` | 模板驅動生成 | ❌ |
| POST | `/api/generate/template/batch` | 批次模板生成 | ❌ |
| POST | `/api/generate/prompt` | Prompt 驅動生成 | ❌ |
| POST | `/api/generate/template-enhanced` | 完整模板生成 | ❌ |

**生成模式說明**：
- **基礎模式** (`/`): 指定科目、題型、數量
- **批次模式** (`/batch`): 並行處理多個請求
- **模板模式** (`/template`): 使用預定義模板
- **Prompt 模式** (`/prompt`): 前端傳入完整 prompt
- **Enhanced 模式** (`/template-enhanced`): 完整模板資訊（含參數）

#### 題目管理 (7 個端點)

| Method | Path | 功能 | Mock |
|--------|------|------|------|
| GET | `/api/questions/` | 題目清單 | ✅ |
| GET | `/api/questions/{id}` | 題目詳情 | ✅ |
| POST | `/api/questions/` | 新增題目 | ❌ |
| PUT | `/api/questions/{id}` | 更新題目 | ❌ |
| DELETE | `/api/questions/{id}` | 刪除題目 | ❌ |
| GET | `/api/questions/stats` | 題目統計 | ❌ |
| POST | `/api/questions/export` | 匯出題目 | ❌ |

#### 模板管理 (7 個端點)

| Method | Path | 功能 | Mock |
|--------|------|------|------|
| GET | `/templates/` | 模板清單 | ✅ |
| GET | `/templates/{id}` | 模板詳情 | ✅ |
| POST | `/templates/` | 新增模板 | ✅ |
| PUT | `/templates/{id}` | 更新模板 | ✅ |
| DELETE | `/templates/{id}` | 刪除模板 | ✅ |
| GET | `/templates/subjects` | 科目清單 | ✅ |
| POST | `/templates/initialize-defaults` | 初始化預設模板 | ✅ |

#### 科目管理 (6 個端點)

| Method | Path | 功能 | Mock |
|--------|------|------|------|
| GET | `/api/subjects/` | 科目清單 | ❌ |
| GET | `/api/subjects/{id}` | 科目詳情 | ❌ |
| POST | `/api/subjects/` | 新增科目 | ❌ |
| PUT | `/api/subjects/{id}` | 更新科目 | ❌ |
| DELETE | `/api/subjects/{id}` | 刪除科目 | ❌ |
| GET | `/api/subjects/usage/stats` | 使用統計 | ❌ |

#### 儀表板 (1 個端點)

| Method | Path | 功能 | Mock |
|--------|------|------|------|
| GET | `/api/dashboard/stats` | 系統統計 | ✅ |

**總計**: 42 個真實端點 + 11 個 Mock 端點

### 3.3 核心服務層詳解

#### 3.3.1 LLM Client (`llm_client.py`)

**職責**: Claude API 整合、題目生成核心邏輯

**核心函數**:
```python
async def generate_questions_by_template(
    template_content: str,
    context: str,
    count: int,
    question_type: str,
    **params
) -> List[Dict]

async def generate_questions_by_prompt(
    prompt: str,
    count: int,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    top_p: float = 1.0,
    frequency_penalty: float = 0.0
) -> List[Dict]

def validate_question_format(
    questions: List[Dict],
    question_type: str
) -> List[Dict]
```

**特色**:
- 詳細的 logging（emoji 標記：🚀🤖✅❌📝）
- 支援多種題型格式驗證
- JSON 解析容錯機制（regex 提取、代碼塊解析）
- 自動題型檢測

#### 3.3.2 Retrieval Service (`retrieval.py`)

**職責**: pgvector 向量相似度搜尋

**核心函數**:
```python
async def search_similar_chunks(
    db: AsyncSession,
    query: str,
    document_id: int,
    top_k: int = 5,
    similarity_threshold: float = 0.1
) -> List[Tuple[Embedding, float]]
```

**SQL 查詢**:
```sql
SELECT
    id, document_id, slice_text, vector, created_at,
    (1 - (vector <=> :query_vector)) as similarity
FROM embeddings
WHERE document_id = :document_id
AND (1 - (vector <=> :query_vector)) > :threshold
ORDER BY similarity DESC
LIMIT :limit
```

**pgvector 運算子**:
- `<=>`: 餘弦距離（Cosine Distance）
- `1 - (vector <=> query)`: 餘弦相似度（0~1，越大越相似）

#### 3.3.3 Ingest Service (`ingest.py`)

**職責**: 文件分塊與向量化

**核心流程**:
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 1. 切分文件
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50
)
chunks = splitter.split_text(document.content)

# 2. 為每個切片生成向量
vectors = await embed_documents(chunks)

# 3. 儲存到 embeddings 表
for txt, vec in zip(chunks, vectors):
    embedding = Embedding(
        document_id=doc_id,
        slice_text=txt,
        vector=vec
    )
    db.add(embedding)
```

### 3.4 題型支援

#### 已實作題型

```mermaid
graph TD
    A[QuestionType Enum] --> B[基礎題型]
    A --> C[G1~G2 擴展題型]
    A --> D[系統題型]

    B --> B1[single_choice 單選題]
    B --> B2[cloze 填空題]
    B --> B3[short_answer 簡答題]

    C --> C1[true_false 是非題]
    C --> C2[matching 配對題]
    C --> C3[sequence 排序題]
    C --> C4[enumeration 列舉題]
    C --> C5[symbol_identification 符號識別題]

    D --> D1[mixed 混合題型]
    D --> D2[auto 自動檢測]

    style C1 fill:#4CAF50
    style C2 fill:#4CAF50
    style C3 fill:#FFA726
    style C4 fill:#FFA726
    style C5 fill:#FFA726
```

**圖例**:
- 🟢 綠色：已實作並完全測試
- 🟠 橙色：部分實作，需前端整合

#### 題型專用資料結構

**配對題 (Matching)**:
```python
class MatchingQuestionData(BaseModel):
    left_items: List[str]   # ["項目A", "項目B", "項目C"]
    right_items: List[str]  # ["定義1", "定義2", "定義3"]
```

**排序題 (Sequence)**:
```python
class SequenceQuestionData(BaseModel):
    items: List[str]  # ["步驟一", "步驟二", "步驟三"]
```

**列舉題 (Enumeration)**:
```python
class EnumerationQuestionData(BaseModel):
    category: str      # "能量形式"
    min_items: int     # 3
    max_items: int     # 5
```

儲存於 `questions.question_data` JSONB 欄位。

### 3.5 依賴套件

**核心依賴**:
```txt
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy[asyncio]==2.0.19
asyncpg==0.28.0
pgvector
anthropic==0.34.2
langchain==0.2.3
python-dotenv==1.0.1
psycopg[binary]==3.1.18
```

**開發依賴**:
```txt
pytest==7.4.0
pytest-asyncio==0.21.0
httpx==0.24.1
ruff==0.0.280
black==23.7.0
pre-commit==3.3.3
```

---

## 4. 前端架構

### 4.1 目錄結構

```
frontend/
├── src/
│   ├── main.js                    # 應用程式入口
│   ├── App.vue                    # 根組件
│   ├── style.css                  # 全域樣式
│   │
│   ├── router/                    # 路由配置
│   │   └── index.js               # Vue Router
│   │
│   ├── views/                     # 頁面級組件
│   │   ├── Dashboard.vue          # 儀表板 (280 行)
│   │   ├── Templates.vue          # 模板管理 (782 行)
│   │   ├── Documents.vue          # 文件管理 (1,092 行)
│   │   ├── Questions.vue          # 題目管理 (2,411 行)
│   │   └── Generate.vue           # 題目生成 (2,222 行)
│   │
│   ├── components/                # 可重用組件
│   │   ├── Sidebar.vue            # 側邊欄導航
│   │   ├── Topbar.vue             # 頂部欄
│   │   ├── Toast.vue              # 通知組件
│   │   ├── Drawer.vue             # 抽屜組件
│   │   ├── SettingsPanel.vue      # 設定面板
│   │   ├── TemplateModal.vue      # 模板編輯模態框
│   │   ├── TemplateViewModal.vue  # 模板檢視模態框
│   │   ├── SubjectModal.vue       # 科目編輯模態框
│   │   ├── ExamDesigner/          # 考券設計器
│   │   │   └── ExamDesigner.vue   # (20,697 行)
│   │   └── ExamPreview/           # 考券預覽
│   │       ├── ExamPreviewModal.vue      # (6,533 行)
│   │       └── SimpleExamPreview.vue     # (18,327 行)
│   │
│   ├── api/                       # API 服務層
│   │   ├── axios.js               # Axios 實例配置
│   │   ├── questionService.js     # 題目相關 API
│   │   ├── documentService.js     # 文件相關 API
│   │   ├── templateService.js     # 模板相關 API
│   │   ├── subjectService.js      # 科目相關 API
│   │   ├── dashboardService.js    # 儀表板統計 API
│   │   └── uploadService.js       # 檔案上傳 API
│   │
│   ├── composables/               # Composition API 可重用邏輯
│   │   └── useLanguage.js         # 多語言支援 Hook
│   │
│   ├── i18n/                      # 國際化
│   │   └── languages.js           # 中英文語言包
│   │
│   ├── utils/                     # 工具函數
│   │   ├── eventBus.js            # 全域事件匯流排
│   │   ├── eventTypes.js          # 事件類型定義
│   │   ├── pdfExporter.js         # PDF 匯出工具
│   │   └── markdownExporter.js    # Markdown 匯出工具
│   │
│   ├── templates/                 # 模板配置
│   │   ├── examTemplates.js       # 考券模板定義
│   │   └── printStyles.css        # 列印專用樣式
│   │
│   └── assets/                    # 靜態資源
│       ├── tailwind.css
│       └── vue.svg
│
├── public/                        # 靜態資源
│   └── vite.svg
│
├── package.json                   # 專案依賴
├── vite.config.js                 # Vite 配置
├── tailwind.config.js             # Tailwind CSS 配置
├── postcss.config.js              # PostCSS 配置
├── nginx.conf                     # Nginx 配置
└── Dockerfile                     # 容器化
```

### 4.2 路由架構

```mermaid
graph TD
    A[/] --> B[Dashboard 儀表板]
    A --> C[/templates]
    A --> D[/documents]
    A --> E[/questions]
    A --> F[/generate]

    C --> C1[Templates.vue]
    D --> D1[Documents.vue]
    E --> E1[Questions.vue]
    F --> F1[Generate.vue]

    C1 --> C2[TemplateModal]
    C1 --> C3[SubjectModal]
    E1 --> E2[ExamDesigner]
    E1 --> E3[ExamPreview]

    style B fill:#42b883
    style C1 fill:#42b883
    style D1 fill:#42b883
    style E1 fill:#42b883
    style F1 fill:#42b883
```

| 路徑 | 組件 | 功能 | 行數 |
|------|------|------|------|
| `/` | Dashboard.vue | 系統儀表板、統計資料、快速操作 | 280 |
| `/templates` | Templates.vue | 模板 CRUD、科目管理、參數配置 | 782 |
| `/documents` | Documents.vue | 文件上傳、管理、搜尋、章節瀏覽 | 1,092 |
| `/questions` | Questions.vue | 題目管理、編輯、匯出、考券設計 | 2,411 |
| `/generate` | Generate.vue | AI 題目生成、模板驅動、批次生成 | 2,222 |

### 4.3 狀態管理策略

**不使用 Pinia/Vuex**，採用輕量級方案：

#### 1. 組件內響應式狀態
```javascript
import { ref, reactive } from 'vue'

const selectedTemplate = ref(null)
const templates = ref([])
const formData = reactive({
  subject: '',
  count: 5
})
```

#### 2. LocalStorage 持久化
```javascript
// 語言設定
localStorage.setItem('language', 'zh')
const currentLanguage = localStorage.getItem('language')
```

#### 3. Props/Emit 父子通信
```vue
<!-- 父組件 -->
<Sidebar :sidebarOpen="sidebarOpen" :menu="menu" />

<!-- 子組件 -->
emit('toggle-sidebar')
```

#### 4. 事件匯流排 (Event Bus)

```mermaid
graph LR
    A[Component A] -->|emit| B[Event Bus]
    B -->|on| C[Component B]
    B -->|on| D[Component C]

    style B fill:#FF6B6B
```

**實作** (`utils/eventBus.js`):
```javascript
import mitt from 'mitt'

const emitter = mitt()

export const TEMPLATE_EVENTS = {
  UPDATED: 'template:updated',
  DELETED: 'template:deleted',
  CREATED: 'template:created'
}

export default {
  emit: emitter.emit,
  on: emitter.on,
  off: emitter.off
}
```

**使用範例**:
```javascript
import eventBus, { TEMPLATE_EVENTS } from '@/utils/eventBus'

// 發送事件
eventBus.emit(TEMPLATE_EVENTS.UPDATED, { templateId: 123 })

// 監聽事件
eventBus.on(TEMPLATE_EVENTS.UPDATED, (data) => {
  console.log('Template updated:', data)
})
```

### 4.4 API 服務層

**Axios 配置** (`api/axios.js`):
```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002',
  headers: { 'Content-Type': 'application/json' }
})

export default api
```

**服務模組範例** (`api/questionService.js`):
```javascript
import api from './axios'

export const generateQuestionsEnhanced = async (requestData) => {
  const response = await api.post('/api/generate/template-enhanced', requestData)
  return response.data
}

export const getQuestions = async (params) => {
  const response = await api.get('/api/questions', { params })
  return response.data
}

export const exportQuestions = async (exportData) => {
  const response = await api.post('/api/questions/export', exportData, {
    responseType: 'blob'
  })

  // 自動下載檔案
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'questions.xlsx')
  document.body.appendChild(link)
  link.click()
  link.remove()
}
```

### 4.5 UI 框架

**Tailwind CSS** - Utility-First 樣式

**配置** (`tailwind.config.js`):
```javascript
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**常見樣式模式**:
```vue
<!-- 卡片 -->
<div class="bg-white shadow rounded-lg p-6">

<!-- 按鈕 -->
<button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md">

<!-- 表單輸入 -->
<input class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500">
```

**無使用 UI 組件庫** (Element Plus、Ant Design Vue 等)，所有組件自行實作。

### 4.6 國際化 (i18n)

**自訂輕量級 i18n 系統**

**Composable** (`composables/useLanguage.js`):
```javascript
import { ref, computed } from 'vue'
import { languages } from '@/i18n/languages'

const currentLanguage = ref(localStorage.getItem('language') || 'zh')

export function useLanguage() {
  const t = (key) => {
    const keys = key.split('.')
    let value = languages[currentLanguage.value]

    for (const k of keys) {
      value = value[k]
      if (!value) return key
    }

    return value
  }

  const setLanguage = (lang) => {
    currentLanguage.value = lang
    localStorage.setItem('language', lang)
  }

  return {
    t,
    currentLanguage,
    setLanguage,
    isEnglish: computed(() => currentLanguage.value === 'en'),
    isChinese: computed(() => currentLanguage.value === 'zh')
  }
}
```

**語言包** (`i18n/languages.js`):
```javascript
export const languages = {
  zh: {
    save: '儲存',
    cancel: '取消',
    nav: {
      dashboard: '儀表板',
      templates: '模板管理',
      documents: '文件管理',
      questions: '題目管理',
      generate: '題目生成'
    }
  },
  en: {
    save: 'Save',
    cancel: 'Cancel',
    nav: {
      dashboard: 'Dashboard',
      templates: 'Templates',
      documents: 'Documents',
      questions: 'Questions',
      generate: 'Generate'
    }
  }
}
```

### 4.7 核心依賴

**運行時依賴** (`package.json`):
```json
{
  "dependencies": {
    "axios": "^1.10.0",
    "jspdf": "^3.0.2",
    "mitt": "^3.0.1",
    "vue": "^3.5.17",
    "vue-router": "^4.5.1"
  }
}
```

**開發依賴**:
```json
{
  "devDependencies": {
    "@vitejs/plugin-vue": "^6.0.0",
    "autoprefixer": "^10.4.21",
    "postcss": "^8.5.6",
    "tailwindcss": "^3.4.17",
    "vite": "^7.0.4"
  }
}
```

**特色**:
- ✅ 極簡依賴（僅 5 個 runtime 依賴）
- ✅ 無笨重 UI 庫
- ✅ 快速構建與啟動

---

## 5. 資料庫設計

### 5.1 資料表結構

```mermaid
erDiagram
    SUBJECTS ||--o{ TEMPLATES : "has many"
    TEMPLATES ||--o{ QUESTIONS : "generates"
    DOCUMENTS ||--o{ EMBEDDINGS : "splits into"
    DOCUMENTS ||--o{ QUESTIONS : "sources"

    SUBJECTS {
        serial id PK
        varchar name UK
        text description
        varchar color
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    TEMPLATES {
        serial id PK
        varchar subject
        integer subject_id FK
        varchar name
        text content
        varchar question_type
        jsonb params
        integer version
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    DOCUMENTS {
        serial id PK
        varchar subject
        varchar title
        text content
        text_array image_urls
        varchar chapter
        varchar page_number
        text image_data
        varchar import_source
        timestamp created_at
        timestamp updated_at
    }

    EMBEDDINGS {
        serial id PK
        integer document_id FK
        text slice_text
        vector_1536 vector
        timestamp created_at
    }

    QUESTIONS {
        serial id PK
        varchar question_type
        text stem
        text_array options
        text answer
        text explanation
        jsonb question_data
        integer document_id FK
        integer template_id FK
        jsonb source_metadata
        varchar export_batch_id
        timestamp created_at
    }
```

### 5.2 詳細欄位說明

#### subjects - 科目表

| 欄位 | 型別 | 說明 | 約束 |
|------|------|------|------|
| id | SERIAL | 主鍵 | PRIMARY KEY |
| name | VARCHAR(50) | 科目名稱 | UNIQUE, NOT NULL |
| description | TEXT | 科目描述 | - |
| color | VARCHAR(7) | UI 顯示顏色 (HEX) | DEFAULT '#3B82F6' |
| is_active | BOOLEAN | 是否啟用 | DEFAULT true |
| created_at | TIMESTAMP | 建立時間 | DEFAULT NOW() |
| updated_at | TIMESTAMP | 更新時間 | DEFAULT NOW() |

**初始資料**: 健康、英文、歷史、數學、自然、國文、地理、公民、資訊、藝術

#### documents - 文件表

| 欄位 | 型別 | 說明 | 約束 |
|------|------|------|------|
| id | SERIAL | 主鍵 | PRIMARY KEY |
| title | VARCHAR(255) | 標題 | NOT NULL |
| content | TEXT | 完整內容 | NOT NULL |
| subject | VARCHAR(50) | 科目 | - |
| chapter | VARCHAR(100) | 章節 | - |
| image_urls | TEXT[] | 圖片 URL 陣列 | PostgreSQL ARRAY |
| image_filename | VARCHAR(255) | 圖片檔名 | - |
| page_number | VARCHAR(20) | 頁碼 | - |
| image_data | TEXT | Base64 圖片資料 | - |
| import_source | VARCHAR(100) | 匯入來源 | DEFAULT 'manual' |
| created_at | TIMESTAMP | 建立時間 | DEFAULT NOW() |
| updated_at | TIMESTAMP | 更新時間 | DEFAULT NOW() |

**索引**: `idx_documents_subject`

#### templates - 模板表

| 欄位 | 型別 | 說明 | 約束 |
|------|------|------|------|
| id | SERIAL | 主鍵 | PRIMARY KEY |
| subject | VARCHAR(50) | 科目 (舊欄位) | - |
| subject_id | INTEGER | 外鍵 | FK → subjects.id |
| name | VARCHAR(100) | 模板名稱 | NOT NULL |
| content | TEXT | Prompt 模板 | NOT NULL |
| question_type | VARCHAR(32) | 題型 | DEFAULT 'single_choice' |
| params | JSONB | LLM 參數 | - |
| version | INTEGER | 版本號 | DEFAULT 1 |
| is_active | BOOLEAN | 是否啟用 | DEFAULT true |
| created_at | TIMESTAMP | 建立時間 | DEFAULT NOW() |
| updated_at | TIMESTAMP | 更新時間 | DEFAULT NOW() |

**索引**: `idx_templates_subject`, `idx_templates_subject_id`, `idx_templates_active`

**params 範例**:
```json
{
  "temperature": 0.7,
  "max_tokens": 2000,
  "top_p": 1.0,
  "frequency_penalty": 0.0
}
```

#### embeddings - 向量嵌入表

| 欄位 | 型別 | 說明 | 約束 |
|------|------|------|------|
| id | SERIAL | 主鍵 | PRIMARY KEY |
| document_id | INTEGER | 所屬文件 | FK → documents.id (CASCADE) |
| slice_text | TEXT | 文本切片 | NOT NULL |
| vector | VECTOR(1536) | pgvector 向量 | - |
| created_at | TIMESTAMP | 建立時間 | DEFAULT NOW() |

**索引**:
- `ix_embeddings_document_id` (B-tree)
- `ix_embeddings_vector` (IVFFlat, vector_cosine_ops) ← **核心向量索引**

**向量索引說明**:
```sql
CREATE INDEX ix_embeddings_vector
ON embeddings
USING ivfflat (vector vector_cosine_ops);
```

#### questions - 題目表

| 欄位 | 型別 | 說明 | 約束 |
|------|------|------|------|
| id | SERIAL | 主鍵 | PRIMARY KEY |
| question_type | VARCHAR(32) | 題型 | NOT NULL |
| stem | TEXT | 題幹 | NOT NULL |
| options | TEXT[] | 選項陣列 | - |
| answer | TEXT | 正確答案 | NOT NULL |
| explanation | TEXT | 解釋 | NOT NULL |
| question_data | JSONB | 題型專用資料 | - |
| document_id | INTEGER | 來源文件 | FK → documents.id (CASCADE) |
| template_id | INTEGER | 使用模板 | FK → templates.id (SET NULL) |
| source_metadata | JSONB | 來源元數據 | - |
| export_batch_id | VARCHAR(50) | 匯出批次 | - |
| created_at | TIMESTAMP | 建立時間 | DEFAULT NOW() |

**索引**:
- `idx_questions_type`, `idx_questions_document_id`, `idx_questions_template_id` (B-tree)
- `idx_questions_data`, `idx_questions_metadata` (GIN) ← JSON 索引

**question_data 範例（配對題）**:
```json
{
  "left_items": ["項目A", "項目B", "項目C"],
  "right_items": ["定義1", "定義2", "定義3"]
}
```

**source_metadata 範例**:
```json
{
  "subject": "健康",
  "chapter": "第一章",
  "page": "12-15",
  "source_content": "原始文本內容..."
}
```

### 5.3 關聯關係

```mermaid
graph TB
    S[subjects] -->|1:N| T[templates]
    T -->|1:N| Q[questions]
    D[documents] -->|1:N| E[embeddings]
    D -->|1:N| Q

    S -.->|ON DELETE SET NULL| T
    D -.->|ON DELETE CASCADE| E
    D -.->|ON DELETE CASCADE| Q
    T -.->|ON DELETE SET NULL| Q

    style D fill:#FFE082
    style E fill:#81C784
    style Q fill:#64B5F6
```

1. **subjects ↔ templates** (1:N): 一個科目有多個模板
2. **templates ↔ questions** (1:N): 一個模板生成多個題目
3. **documents ↔ embeddings** (1:N, CASCADE): 一個文件切分為多個向量
4. **documents ↔ questions** (1:N, CASCADE): 一個文件生成多個題目

**級聯刪除策略**:
- 刪除 `documents` → 自動刪除相關 `embeddings` 和 `questions`
- 刪除 `templates` → 相關 `questions` 的 `template_id` 設為 NULL
- 刪除 `subjects` → 相關 `templates` 的 `subject_id` 設為 NULL

### 5.4 pgvector 向量檢索

#### 向量索引建立

```sql
-- IVFFlat 索引（近似最近鄰搜尋）
CREATE INDEX ix_embeddings_vector
ON embeddings
USING ivfflat (vector vector_cosine_ops)
WITH (lists = 100);
```

**參數調優**:
- `lists`: 分區數量，建議 `sqrt(總列數)`
  - 1,000 筆 → lists = 32
  - 10,000 筆 → lists = 100
  - 100,000 筆 → lists = 316

**查詢優化**:
```sql
SET ivfflat.probes = 10;  -- 探測分區數（越大越精確但越慢）
```

#### 相似度搜尋範例

```sql
-- 找出與特定向量最相似的前 10 個切片
SELECT
    id,
    slice_text,
    (1 - (vector <=> '[0.1, 0.2, ...]'::vector)) as similarity
FROM embeddings
WHERE document_id = 123
ORDER BY vector <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;
```

**pgvector 運算子**:
- `<=>`: 餘弦距離（Cosine Distance）
- `<->`: 歐幾里得距離（L2 Distance）
- `<#>`: 內積（Negative Inner Product）

### 5.5 資料庫初始化

**初始化腳本**: `/backend/db/init_complete.sql`

**版本管理**:
```sql
CREATE TABLE schema_version (
    version VARCHAR(20) PRIMARY KEY,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_version (version, description) VALUES
('2.0.0', '完整資料庫結構 - 支援 G1/G2 題型與科目管理');
```

**健康檢查函數**:
```sql
CREATE OR REPLACE FUNCTION check_database_health()
RETURNS TABLE(
    table_name TEXT,
    row_count BIGINT,
    status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'subjects'::TEXT, COUNT(*)::BIGINT,
           CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'EMPTY' END::TEXT
    FROM subjects
    UNION ALL
    SELECT 'templates'::TEXT, COUNT(*)::BIGINT,
           CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'EMPTY' END::TEXT
    FROM templates;
    -- ... 其他表
END;
$$ LANGUAGE plpgsql;

-- 使用
SELECT * FROM check_database_health();
```

### 5.6 效能考量

#### 資料量估算

假設 1,000 篇文件：

| 項目 | 計算 | 結果 |
|-----|------|------|
| 文件數 | 1,000 篇 | 1,000 列 |
| 平均長度 | 5,000 字元 | - |
| 切片大小 | 300 字元/切片 | - |
| 每篇切片數 | 5,000 / 300 ≈ 17 | - |
| 總向量數 | 1,000 × 17 | 17,000 列 |
| 向量維度 | OpenAI ada-002 | 1,536 維 |
| 單一向量大小 | 1,536 × 4 bytes | 6 KB |
| 總向量儲存 | 17,000 × 6 KB | ~100 MB |

#### 查詢優化策略

1. **限制檢索範圍**:
```sql
-- ✅ 好：先過濾 document_id
WHERE document_id = :doc_id
AND (1 - (vector <=> :query)) > :threshold

-- ❌ 差：全表向量搜尋
WHERE (1 - (vector <=> :query)) > :threshold
```

2. **調整相似度閾值**:
- 高閾值 (0.7~1.0): 精準但可能遺漏
- 低閾值 (0.1~0.3): 覆蓋廣但有噪音

3. **使用連線池**:
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

---

## 6. 部署架構

### 6.1 Docker 服務編排

#### 開發環境 (docker-compose.yml)

```mermaid
graph TB
    subgraph "Docker Network: edurag_network"
        FE[frontend:3000<br/>Vue 3 + Nginx]
        BE[backend:8000<br/>FastAPI]
        PG[(postgres:5432<br/>PostgreSQL + pgvector)]
        PA[pgadmin:5050<br/>pgAdmin]
    end

    U[開發者] -->|http://localhost:3000| FE
    U -->|http://localhost:8000| BE
    U -->|http://localhost:5050| PA

    FE -->|API Proxy| BE
    BE -->|AsyncPG| PG
    PA -->|Manage| PG

    style FE fill:#42b883
    style BE fill:#009688
    style PG fill:#336791
    style PA fill:#4A90E2
```

**服務清單**:

| 服務 | 映像 | Port | 功能 |
|------|------|------|------|
| frontend | Nginx + Vue | 3000 | 前端 SPA |
| backend | FastAPI | 8000 | 後端 API |
| postgres | pgvector/pgvector:pg15 | 5432 | 資料庫 |
| pgadmin | dpage/pgadmin4 | 5050 | DB 管理工具 |

**Volume 掛載**:
- `postgres_data:/var/lib/postgresql/data` - 資料持久化
- `./backend:/app` - 熱重載
- `./frontend:/app` - 熱重載

**健康檢查**:
```yaml
postgres:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U edurag_user"]
    interval: 10s
    timeout: 5s
    retries: 5
```

#### 生產環境 (docker-compose.prod.yml)

```mermaid
graph TB
    subgraph "Docker Network: edurag_network"
        NG[nginx:80/443<br/>反向代理 + SSL]
        FE[frontend:3000<br/>靜態資源]
        BE[backend:8000<br/>FastAPI x2 Workers]
        PG[(postgres:5432<br/>PostgreSQL)]
    end

    INT[公網] -->|HTTPS| NG
    NG -->|Proxy| FE
    NG -->|/api/| BE
    BE -->|AsyncPG| PG

    style NG fill:#43A047
    style FE fill:#42b883
    style BE fill:#009688
    style PG fill:#336791
```

**差異**:

| 項目 | 開發環境 | 生產環境 |
|------|---------|----------|
| Backend Workers | 1 (--reload) | 2 |
| Nginx | 前端內建 | 獨立服務（SSL） |
| pgAdmin | 啟用 | 停用 |
| Volume Mount | 雙向 | 單向 |
| 日誌限制 | 無 | 10MB / 3 檔 |
| 健康檢查 | 基本 | 完整（含 curl） |

### 6.2 環境變數配置

#### 核心環境變數

```bash
# 應用程式模式
USE_MOCK_API=false                    # true=Mock, false=真實

# 資料庫
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=edurag
POSTGRES_USER=edurag_user
POSTGRES_PASSWORD=<SECURE_PASSWORD>
DATABASE_URL=postgresql+asyncpg://edurag_user:<PASSWORD>@postgres:5432/edurag

# LLM Provider
LLM_PROVIDER=anthropic                # 支援: anthropic / openai
ANTHROPIC_API_KEY=<YOUR_API_KEY>      # 必填（非 Mock 模式）
OPENAI_API_KEY=<YOUR_API_KEY>         # 可選

# CORS
CORS_ORIGINS=http://localhost:3000    # 生產環境應設為實際域名

# 向量配置
VECTOR_DIMENSION=1536                 # OpenAI ada-002 維度

# 日誌
LOG_LEVEL=INFO                        # DEBUG / INFO / WARNING / ERROR
```

#### 配置載入流程

```mermaid
sequenceDiagram
    participant E as .env 檔案
    participant D as dotenv
    participant C as config.py
    participant A as app.main

    A->>C: 匯入配置
    C->>D: load_dotenv()
    D->>E: 讀取環境變數
    E-->>D: 回傳變數
    D-->>C: os.getenv()

    alt USE_MOCK_API=true
        C-->>A: 載入 Mock 路由
    else USE_MOCK_API=false
        C->>C: 驗證必要變數
        alt 缺少 DATABASE_URL
            C-->>A: RuntimeError
        else 缺少 ANTHROPIC_API_KEY
            C-->>A: RuntimeError
        else 完整
            C-->>A: 載入真實路由
        end
    end
```

### 6.3 CORS 與安全配置

#### CORS 設定

**後端** (`backend/app/main.py`):
```python
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**問題與建議**:
- ⚠️ 僅允許 `5173/5174`，但 docker-compose 使用 Port 3000
- ⚠️ 生產環境應從環境變數讀取 `CORS_ORIGINS`

**建議修正**:
```python
import os

origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
```

#### 安全要點

1. **API Key 管理**:
   - ✅ 使用 `.env` 檔案
   - ✅ `.env` 已加入 `.gitignore`
   - 🔧 建議使用 Docker Secrets（生產環境）

2. **資料庫安全**:
   - ✅ 生產環境使用 md5 認證
   - ✅ 限制 Port 僅內部網路存取
   - ⚠️ 開發環境使用 `trust` 認證（無密碼）

3. **日誌安全**:
   - 🔧 確保日誌不含 API Key、密碼
   - 🔧 日誌檔案權限設為 640

4. **健康檢查端點**:
   - ✅ `/health` 不暴露敏感資訊
   - 🔧 建議加上認證保護

### 6.4 部署流程

#### 開發環境啟動

```bash
# 1. 複製環境變數
cp .env.example .env

# 2. 編輯 .env
vim .env  # 填入 ANTHROPIC_API_KEY

# 3. 啟動所有服務
docker-compose up -d

# 4. 初始化資料庫
./scripts/db-init.sh init

# 5. 檢查服務狀態
docker-compose ps
curl http://localhost:8000/health

# 訪問服務
# - 前端: http://localhost:3000
# - 後端: http://localhost:8000
# - pgAdmin: http://localhost:5050
```

#### 生產環境部署

```bash
# 1. 建立生產環境變數
cp .env.example .env.prod
vim .env.prod  # 設定強密碼、域名、CORS

# 2. 啟動生產環境
docker-compose -f docker-compose.prod.yml up -d

# 3. 初始化資料庫
./scripts/db-init.sh init

# 4. 配置 SSL 證書（Let's Encrypt）
certbot certonly --webroot -w /var/www/certbot -d edurag.example.com

# 5. 檢查服務健康
curl https://edurag.example.com/health
```

#### CI/CD 建議

**GitHub Actions 工作流程** (`.github/workflows/backend-test.yml`):
```yaml
name: Backend Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: pgvector/pgvector:pg15
        env:
          POSTGRES_DB: edurag_test
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests
        env:
          DATABASE_URL: postgresql+asyncpg://test_user:test_pass@localhost/edurag_test
          USE_MOCK_API: true
        run: |
          cd backend
          pytest tests/ -v
```

---

## 7. 開發規範

### 7.1 規格驅動開發流程

#### 四階段關卡（必遵循）

```mermaid
graph TD
    A[A. Requirements 審核] -->|✅ 通過| B[B. Design 審核]
    A -->|❌ 不足| A1[補充使用者故事與驗收條件]
    A1 --> A

    B -->|✅ 通過| C[C. Tasks 分解]
    B -->|❌ 風險| B1[提出緩解措施]
    B1 --> B

    C -->|✅ 通過| D[D. Execute 實作]
    C -->|❌ 不明確| C1[標註產物與依賴]
    C1 --> C

    D --> E[產出程式碼]
    D --> F[撰寫測試]
    D --> G[更新文件]

    style A fill:#FF6B6B
    style B fill:#4ECDC4
    style C fill:#FFE66D
    style D fill:#95E1D3
```

#### A) Requirements 審核

**檢查項目**:
- [ ] 使用者故事是否充分可測？
- [ ] 驗收條件是否明確？
- [ ] 效能指標是否定義？
- [ ] 安全與品質要求是否完整？

**來源文件**: `specs/requirements.md`, `specs/requirements_updated.md`

#### B) Design 審核

**檢查項目**:
- [ ] 架構設計是否清晰？
- [ ] 模組邊界是否明確？
- [ ] 資料模型是否完整？
- [ ] 風險是否識別並緩解？

**來源文件**: `specs/design.md`, `specs/design_updated.md`

#### C) Tasks 分解

**檢查項目**:
- [ ] 任務是否可執行？
- [ ] 任務是否可並行？
- [ ] 預期產物是否標註？
- [ ] 技術依賴是否識別？

**來源文件**: `specs/tasks.md`, `specs/tasks_updated.md`

#### D) Execute 實作

**實作要求**:
- ✅ 僅在 A~C ✅ 後才產出程式碼
- ✅ 程式碼需符合 steering 規範
- ✅ Mock 模式優先產出 stub/fixtures
- ✅ 附上執行、測試、觀測方法

### 7.2 Steering 規範

#### 產品規範 (product.md)

**核心 KPI**:
- TTFQ (Time To First Question) P95 < 8s
- Mock 模式 TTFQ P95 < 2s
- 檢索相關度@5 ≥ 0.7
- 生成錯誤率 P95 < 2%
- 前端互動延遲 P95 < 200ms

#### 技術規範 (tech.md)

**後端規範**:
- 語言：Python 3.11+
- 框架：FastAPI + SQLAlchemy (async)
- 命名：snake_case
- Schema：Pydantic 嚴格驗證
- 日誌：結構化 JSON 格式

**前端規範**:
- 語言：JavaScript ES6+
- 框架：Vue 3 (Composition API)
- 命名：kebab-case (檔案)、camelCase (變數)
- 樣式：Tailwind CSS Utility-First

**API 規範**:
- RESTful 風格
- CORS 僅允許指定來源
- request-id 追蹤
- 統一錯誤格式

#### 結構規範 (structure.md)

**目錄結構**:
```
backend/
  app/
    api/         # 路由/控制器
    core/        # 設定、LLM
    services/    # 業務邏輯
    repos/       # DB 存取
    schemas/     # Pydantic
    db/          # models、session

frontend/
  src/
    components/
    pages/
    composables/
    services/
```

**命名慣例**:
- Python：`snake_case`
- 前端檔案：`kebab-case.vue`
- 前端變數：`camelCase`
- API：RESTful 風格

### 7.3 程式碼品質

#### Linting & Formatting

**後端**:
```bash
# Ruff (快速 Linter)
ruff check backend/app/

# Black (格式化)
black backend/app/

# Pre-commit
pre-commit install
pre-commit run --all-files
```

**前端**:
```bash
# ESLint
npm run lint

# Prettier
npm run format
```

#### 測試

**後端測試**:
```bash
cd backend
pytest tests/ -v --cov=app
```

**測試檔案結構**:
```
tests/
├── test_health.py          # 健康檢查
├── test_mock_apis.py       # Mock API 測試
├── test_templates.py       # 模板 CRUD
└── test_generate.py        # 題目生成
```

**前端測試** (待實作):
```bash
cd frontend
npm run test
```

---

## 8. 技術決策

### 8.1 核心技術決策

#### 1. LLM Provider：Anthropic Claude

**決策**:
```python
# backend/app/core/config.py
LLM_PROVIDER = "anthropic"
```

**理由**:
- ✅ 高品質輸出
- ✅ 繁體中文支援良好
- ✅ Context Window 大（200K tokens）

**彈性**: 保留可替換界面

#### 2. 資料庫：PostgreSQL + pgvector

**決策**: 統一使用 PostgreSQL + pgvector

**優點**:
- ✅ 部署簡化（無需額外向量庫）
- ✅ ACID 保證
- ✅ 向量搜尋整合

**缺點與緩解**:
- ⚠️ 向量資料量暴增可能影響效能
- 🔧 緩解：日後可抽離向量庫（如 Qdrant）

#### 3. Mock 模式支援

**決策**: 完整支援 Mock API 模式

**要求**:
- ✅ 嚴格維持與真實 API schema 一致
- ✅ 獨立 mock_*.py 路由器
- ✅ Fixtures 資料與真實資料結構一致

**價值**:
- 提升前端效率
- 降低開發依賴
- 支援離線開發

#### 4. 題型資料結構：JSONB

**決策**: 使用 `question_data` JSONB 欄位

**優點**:
- ✅ Schema 彈性
- ✅ 向後相容
- ✅ 易於擴展

**缺點與緩解**:
- ⚠️ 查詢複雜度增加
- 🔧 緩解：Pydantic 模型強制型別檢查、GIN 索引

#### 5. 圖片儲存：混合策略

**決策**:
- 小圖片（< 1MB）：base64 存入 DB
- 大圖片（≥ 1MB）：檔案系統 + 路徑存入 DB

**優點**: 平衡效能與資料完整性

### 8.2 架構取捨

#### LangChain vs 自行串接

```mermaid
graph LR
    A[選擇 LangChain] --> B[優點]
    A --> C[缺點]

    B --> B1[加速串接]
    B --> B2[鏈式處理]
    B --> B3[社群生態]

    C --> C1[抽象層較厚]
    C --> C2[升級風險]

    D[緩解措施] --> D1[保留可替換界面]

    style A fill:#4CAF50
    style D fill:#FFA726
```

**決策**: ✅ 使用 LangChain

#### 同步 vs 非同步處理

**決策**: 批量操作採用**同步處理**

**理由**:
- ✅ 避免增加 Celery/Redis 複雜度
- ✅ 簡化部署

**缺點與緩解**:
- ⚠️ 大批量可能阻塞
- 🔧 緩解：檔案大小限制（50MB）、進度提示

#### 題型實作優先序

```mermaid
graph LR
    P1[Phase 1] --> T1[true_false]
    P1 --> T2[matching]

    P2[Phase 2] --> T3[sequence]
    P2 --> T4[enumeration]

    P3[Phase 3] --> T5[symbol_identification]

    P4[Future] --> T6[image_based_qa]

    style P1 fill:#4CAF50
    style P2 fill:#FFA726
    style P3 fill:#42A5F5
    style P4 fill:#9E9E9E
```

### 8.3 效能指標

| 指標 | 目標值 | 說明 |
|------|--------|------|
| TTFQ (真實模式) | P95 < 8s | Time To First Question |
| TTFQ (Mock 模式) | P95 < 2s | Mock 回應時間 |
| Excel 匯入 | P95 < 30s | < 50MB 檔案 |
| 批量匯出 | P95 < 10s | 100 題內 |
| 多文件生成 | P95 < 15s | 最多 20 文件 |
| 前端互動 | P95 < 200ms | 點擊至回應 |
| 檢索相關度@5 | ≥ 0.7 | Top-5 相關度 |
| 生成錯誤率 | P95 < 2% | JSON 解析失敗率 |

### 8.4 安全考量

#### 1. 檔案上傳

- ✅ MIME 驗證
- ✅ 大小限制（50MB）
- 🔧 待加強：惡意內容掃描

#### 2. Prompt Injection

- ✅ 輸入清理
- ✅ 長度限制
- 🔧 待加強：關鍵詞過濾

#### 3. API 安全

- ✅ CORS 控制
- ✅ request-id 追蹤
- 🔧 待加強：速率限制（Rate Limiting）

---

## 附錄

### A. 常用指令

#### Docker 操作

```bash
# 開發環境
docker-compose up -d                          # 啟動
docker-compose logs -f backend                # 查看日誌
docker-compose exec backend bash              # 進入容器
docker-compose down                           # 停止

# 生產環境
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs --tail=100
```

#### 資料庫管理

```bash
./scripts/db-init.sh init                     # 初始化
./scripts/db-init.sh reset                    # 重置
./scripts/db-init.sh check                    # 健康檢查
./scripts/db-init.sh backup                   # 備份
./scripts/db-init.sh restore backup/file.sql  # 還原

# 直接連線
docker exec edurag_postgres psql -U edurag_user -d edurag
```

#### 開發工具

```bash
# 後端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 測試
pytest tests/ -v --cov=app

# Lint
ruff check app/
black app/

# 前端
cd frontend
npm install
npm run dev

# 構建
npm run build
```

### B. 關鍵檔案路徑

```
專案根目錄: /Users/wangshanchi/SideProjects/abraham/EduRAG/

規範文件:
├── .claude/steering/product.md
├── .claude/steering/tech.md
└── .claude/steering/structure.md

需求設計:
├── specs/requirements.md
├── specs/requirements_updated.md
├── specs/design.md
├── specs/design_updated.md
├── specs/tasks.md
└── specs/tasks_updated.md

核心代碼:
├── backend/app/main.py
├── backend/app/core/config.py
├── backend/app/core/llm_client.py
├── backend/app/db/models.py
├── frontend/src/App.vue
├── frontend/src/api/axios.js
└── frontend/src/router/index.js

配置檔案:
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
└── backend/db/init_complete.sql
```

### C. 重要 URL

**開發環境**:
- 前端：http://localhost:3000
- 後端 API：http://localhost:8000
- API 文件：http://localhost:8000/docs
- 健康檢查：http://localhost:8000/health
- pgAdmin：http://localhost:5050

**生產環境**:
- 入口：https://edurag.example.com
- API：https://edurag.example.com/api
- 健康檢查：https://edurag.example.com/health

---

## 版本歷史

| 版本 | 日期 | 變更說明 |
|------|------|---------|
| 2.0.0 | 2025-10-11 | 完整架構文件初版，涵蓋前後端、資料庫、部署 |

---

**文件維護**: 此文件應隨專案演進持續更新，確保與實際實作保持同步。