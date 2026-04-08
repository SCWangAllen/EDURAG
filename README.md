# EduRAG

RAG-based educational question generation system. Teachers upload course materials, which are chunked, embedded, and used to generate various exam question types via LLM.

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy (async) + PostgreSQL + pgvector
- **Frontend**: Vue 3 (Composition API) + Vite + Tailwind CSS
- **LLM**: Anthropic Claude via LangChain
- **Infrastructure**: Docker Compose

## Features

- Document ingestion with automatic chunking and vector embedding (1536-dim)
- 10 question types: single choice, cloze, short answer, true/false, matching, sequence, enumeration, symbol identification, mixed, auto
- Template-based question generation with subject/grade management
- Exam paper designer with drag-and-drop question selection
- Export to PDF and Markdown
- Mock mode for development without DB/LLM dependencies

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Using Docker (recommended)

```bash
# Copy environment variables
cp .env.example .env
# Edit .env with your API keys and database credentials

# Start all services
docker-compose up -d
```

Services will be available at:
- Frontend: http://localhost:8989
- Backend API: http://localhost:8988
- pgAdmin: http://localhost:5055

### Local Development

**Backend**:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Mock mode (no DB/LLM needed)
USE_MOCK_API=true uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

### Database Setup

```bash
# Initialize database
./scripts/db-init.sh init

# Apply migrations
cd backend
alembic upgrade head
```

## Project Structure

```
backend/
  app/
    core/         # Config, LLM client, embeddings
    routers/      # API route handlers (+ mock variants)
    services/     # Business logic
    schemas/      # Pydantic models
    db/           # SQLAlchemy models, database setup
    prompts/      # LLM prompt templates
  db/init.sql     # Database schema (source of truth)

frontend/src/
  views/          # Page components
  components/     # Shared UI components
  api/            # Axios service layer
  composables/    # Reusable composition functions
  utils/          # Helpers (PDF export, event bus, etc.)
  i18n/           # Internationalization (zh/en)
```

## Environment Variables

See `.env.example` for all available configuration options. Key variables:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL async connection string |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key |
| `USE_MOCK_API` | Set `true` for mock mode (no DB/LLM) |
| `VITE_API_BASE_URL` | Frontend API base URL override |

## License

All rights reserved.
