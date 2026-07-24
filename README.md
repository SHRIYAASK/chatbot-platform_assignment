# Chatbot Platform

A production-oriented AI chatbot platform where each project is a configurable AI assistant.

- **Backend:** FastAPI · SQLAlchemy · PostgreSQL · Alembic · JWT · Groq
- **Frontend:** React · Vite · Tailwind
- **Architecture:** Modular monolith (`authentication`, `workspace`, `prompt_management`, `chat` with RAG, `shared`)

---

## Quick start with Docker (recommended)

Requires Docker + Docker Compose. This starts Postgres, runs migrations automatically, and serves the API and frontend.

```bash
# From the repository root
export GROQ_API_KEY=your-groq-api-key
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(48))")

docker compose up --build
```

- Frontend: http://localhost:8080
- API: http://localhost:8002
- API docs: http://localhost:8002/docs

> On Windows PowerShell, set variables with `$env:GROQ_API_KEY="..."` and `$env:SECRET_KEY="..."` before running compose.

---

## Local development

### Prerequisites
- Python 3.13+, Node.js 20+, PostgreSQL 14+

### Backend

```bash
cd backend
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1   |   Unix: source venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env      # then edit values (see below)
uvicorn app.main:app --host 127.0.0.1 --port 8002
```

Migrations run automatically on startup when `AUTO_MIGRATE=true` (default for local dev). You can still run them manually:

```bash
alembic upgrade head
```

Required `.env` values:
- `DATABASE_URL` — PostgreSQL connection string
- `SECRET_KEY` — strong random value, **at least 32 characters** (placeholders are rejected at startup)
- `GROQ_API_KEY` — required for chat responses
- `EMBEDDING_API_KEY` — Hugging Face token for document search/RAG ([create one here](https://huggingface.co/settings/tokens))

### Frontend

```bash
cd frontend
npm install
echo "VITE_API_URL=http://127.0.0.1:8002" > .env
npm run dev
```

---

## Testing

The backend test suite runs against an isolated SQLite database (no Postgres needed):

```bash
cd backend
python -m pytest
```

---

## Operational endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Deep health check (DB connectivity) |
| `GET /health/live` | Liveness probe |
| `GET /health/ready` | Readiness probe (dependencies reachable) |

## Notable production features

- Startup validation of `SECRET_KEY` (rejects known placeholders / short keys)
- Structured logging (`LOG_JSON=true` for JSON logs)
- Centralized exception handling (no stack traces leak to clients)
- Tunable DB connection pool (`DB_POOL_*` settings)
- Alembic migrations as the single source of truth for schema
- Input/output guardrails and moderation (`MODERATION_ENABLED`)
