# EduRAG

RAG-based educational question generation system. Teachers upload course materials, which are chunked, embedded, and used to generate various exam question types via LLM.

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy (async) + PostgreSQL + pgvector
- **Frontend**: Vue 3 (Composition API) + Vite + Tailwind CSS
- **LLM**: Anthropic Claude (official `anthropic` SDK)
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

- Docker Desktop (or Docker Engine + Compose v2). **The daemon must be running**: `docker info` has to succeed before anything below.
- An Anthropic API key.
- Node.js 18+ / Python 3.11+ only if you run the frontend/backend outside Docker.

### Using Docker (recommended)

```bash
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY (required) and change the passwords.
# Opening the app from another device? Also set CORS_ORIGINS — see below.

docker compose up -d --build
# First start pulls images and runs backend/db/init.sql on the empty database.

docker compose exec backend alembic stamp head
# FIRST START ONLY (fresh database). See "Database Setup" for why.

curl http://localhost:8988/health
# expect {"status":"healthy", ..., "database_connected": true}
```

Services:
- Frontend: http://localhost:8989
- Backend API: http://localhost:8988 (Swagger UI at `/docs`)
- pgAdmin: http://localhost:5055 — bound to 127.0.0.1 only
- PostgreSQL: 127.0.0.1:5435 — bound to 127.0.0.1 only (`POSTGRES_PORT` to change)

Day-to-day:

```bash
docker compose logs -f backend            # backend logs
docker compose up -d --build frontend     # rebuild after changing frontend/ code (backend hot-reloads)
docker compose down                       # stop; data stays in the postgres_data volume
```

### Accessing from other devices (LAN / another machine)

The browser calls the backend directly at `http://<host>:8988`, so the backend must allow that origin. In `.env`:

```
CORS_ORIGINS=http://192.168.1.10:8989,http://localhost:8989,http://127.0.0.1:8989
```

Comma-separated, no spaces, scheme + host + port, one entry per origin the browser actually uses (IP, hostname or domain). Wildcards are not supported. Apply with `docker compose up -d --force-recreate backend`.

> **Security:** the API has **no authentication**. Anyone who can reach ports 8988/8989 can read, upload and delete data and spend your Anthropic quota. Do not expose them to the public internet without a firewall, VPN or an authenticating reverse proxy. PostgreSQL and pgAdmin are bound to 127.0.0.1 and are never reachable from other machines. For a public hostname with HTTPS and a password, see the Caddy section below.

### Public domain with HTTPS + password (Caddy)

Use this when teachers open the app through a real hostname (e.g. `exam.example.com`) without a VPN. Caddy sits in front of the production stack, obtains a Let's Encrypt certificate automatically and asks for a shared username/password. Frontend and backend ports are bound to 127.0.0.1 so nothing bypasses the password.

Prerequisites:
1. DNS: an `A` record for the hostname pointing at this machine's public IP (static IP, or DDNS).
2. Router/firewall: forward **80 and 443** to this machine. Do **not** forward 8988/8989.
3. `.env`: `SITE_DOMAIN=exam.example.com`.
4. Credentials file (gitignored):
   ```bash
   docker run --rm caddy:2-alpine caddy hash-password --plaintext 'YourPassword'
   # write into caddy/users as one line:   teacher <hash>      (template: caddy/users.example)
   ```

Start the production stack with the Caddy overlay (Docker Compose 2.24+):

```bash
export COMPOSE_FILE=docker-compose.prod.yml:docker-compose.caddy.yml   # makes every `docker compose` below use both files
docker compose up -d --build
docker compose exec backend alembic stamp head     # first start on an EMPTY database only
docker compose logs -f caddy                       # watch the certificate being issued
```

Open `https://exam.example.com` and log in with the credentials from `caddy/users`. API calls are same-origin, so the browser sends the credentials automatically and `CORS_ORIGINS` is not needed.

Switching from the dev stack on the same machine: run `docker compose down --remove-orphans` (with the dev files) first. The database volume `edurag_postgres_data` is shared, so data is kept.

### Local Development (app outside Docker)

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

Schema authority is `backend/app/db/models.py` + Alembic migrations in `backend/alembic/`. `backend/db/init.sql` is a snapshot of the same schema, used only to bootstrap an **empty** database.

**Fresh database (first `docker compose up`)** — Postgres runs `init.sql` automatically. It already contains everything the migrations would add, so mark the database as current instead of upgrading:

```bash
docker compose exec backend alembic stamp head
```

`alembic upgrade head` on a fresh init.sql database fails with `relation "image_questions" already exists`.

**Existing database (after pulling new code)**:

```bash
docker compose exec backend alembic upgrade head
```

**Helper script** (check / backup / restore / reset):

```bash
bash scripts/db-init.sh check
bash scripts/db-init.sh backup
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
  db/init.sql     # Bootstrap snapshot for an empty DB (schema authority: app/db/models.py + alembic/)

frontend/src/
  views/          # Page components
  components/     # Shared UI components
  api/            # Axios service layer
  composables/    # Reusable composition functions
  utils/          # Helpers (PDF export, event bus, etc.)
  i18n/           # Internationalization (zh/en)
```

## Environment Variables

All variables live in the root `.env`, read by Docker Compose. See `.env.example`.

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | yes | Anthropic API key. The backend refuses to start without it unless `USE_MOCK_API=true`. |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | yes | Database credentials. Compose builds the backend's `DATABASE_URL` from them. |
| `CORS_ORIGINS` | when accessed from other devices | Comma-separated browser origins allowed to call the API. |
| `USE_MOCK_API` | no | `true` runs the backend without DB/LLM (mock routers). |
| `BACKEND_PORT` / `FRONTEND_PORT` | no | Host ports, default 8988 / 8989. |
| `POSTGRES_PORT` / `PGADMIN_PORT` | no | Host ports bound to 127.0.0.1 only, default 5435 / 5055. |
| `LLM_MODEL_NAME` | no | Claude model id; default set in `backend/app/core/config.py`. Put it in `backend/.env` (mounted into the container). |
| `VITE_API_BASE_URL` | no | Frontend build-time override of the API base URL. |

## License

All rights reserved.
