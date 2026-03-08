# AI Test Engineer Agent — Project Instructions

## Project Overview
AI-powered tool with 3 core methods:
1. **Document → Test Cases**: Upload PDF/DOCX/MD/TXT → AI generates structured test cases
2. **Test Cases → Scripts**: Convert test cases to Playwright/Artillery automation scripts
3. **URL → Auto-Test → Report**: Provide website URL → AI crawls, tests all modules, finds bugs automatically

## Tech Stack
- **Backend:** FastAPI 0.115.6, Python 3.11+, Uvicorn
- **Database:** PostgreSQL 16 + SQLAlchemy 2.0 (async) + asyncpg
- **Migrations:** Alembic 1.14.1
- **AI Providers:** Google Gemini 2.5 Flash (free), Groq Llama 3.3 70B (free), Ollama (local)
- **Document Parsing:** PyMuPDF (PDF), python-docx (DOCX)
- **Export:** openpyxl (Excel), CSV
- **Testing:** pytest + pytest-asyncio + httpx
- **Linting:** ruff
- **Containerization:** Docker + docker-compose
- **Future:** Redis (cache + task queue), Celery (background workers), Playwright (browser automation), pgvector (vector search)

## Architecture (7 Layers)
```
Layer 1: app/main.py              → FastAPI entry point
Layer 2: app/api/v1/              → Route endpoints
Layer 3: app/schemas/             → Pydantic validation
Layer 4: app/services/            → Business logic
Layer 5: app/ai/                  → AI engine (LLM integration)
Layer 6: app/models/              → SQLAlchemy ORM models
Layer 7: app/db/repositories/     → Data access (CRUD)
```

## Database Schema
- **projects** → top-level container
- **documents** → uploaded files (FK → projects)
- **test_cases** → AI-generated test cases (FK → projects, documents). `test_steps` is a JSONB column.
- **scripts** → automation scripts (FK → test_cases) — Phase 2

## Key Patterns
- Async everywhere: `async def` + `await` in routes, services, repositories
- Dependency injection via FastAPI `Depends()`
- Repository pattern for database access
- Strategy pattern for LLM provider switching (Gemini/Groq/Ollama)
- Pydantic v2 for request/response validation
- Singleton instances for AI components (llm_client, document_analyzer, testcase_generator)

## API Endpoints
- `POST /api/v1/projects/` — Create project
- `GET /api/v1/projects/` — List projects
- `POST /api/v1/documents/upload` — Upload document
- `POST /api/v1/documents/{id}/analyze` — Analyze document with AI
- `POST /api/v1/testcases/generate` — Generate test cases from document
- `GET /api/v1/testcases/` — List test cases (filterable)
- `PUT /api/v1/testcases/{id}` — Update/approve/reject test case
- `GET /api/v1/testcases/export` — Export as CSV/Excel
- `GET /health` — Health check

## Development Phases
- **Phase 1:** Document → Test case generation (IMPLEMENTED)
- **Phase 2:** Test cases → Playwright + Artillery script generation
- **Phase 3:** URL → Auto-crawl → Auto-test → Bug report (the game changer)

## Phase 1 Implementation Status (DONE)
- LLM Client: Gemini 2.5 Flash, Groq, Ollama — all implemented (app/ai/llm_client.py)
- Document Analyzer: PDF/DOCX/MD/TXT extraction + AI analysis (app/ai/document_analyzer.py)
- Test Case Generator: AI-powered generation with prompt templates (app/ai/testcase_generator.py)
- Services wired to AI engine (document_service.py, testcase_service.py)
- Alembic migration created (alembic/versions/001_initial_schema.py)

## TODO (Next Steps)
- Script generator (Phase 2 — Playwright/Artillery)
- URL-based auto-testing (Phase 3)
- Background tasks (Celery + Redis)
- Authentication (JWT)
- pgvector for duplicate test case detection
- Frontend (React/Next.js)

## Commands
- **Run server:** `uvicorn app.main:app --reload`
- **Run with Docker:** `docker-compose up`
- **Run migrations:** `alembic upgrade head`
- **Run tests:** `pytest tests/`
- **Lint:** `ruff check app/`
- **Format:** `ruff format app/`
- **Swagger docs:** http://localhost:8000/docs

## File Storage
- Uploads: `uploads/{project_id}/{filename}`
- Exports: `exports/`

## Configuration
- Settings: `app/config.py` (reads from `.env`)
- Template: `.env.example`
- DB URL: `postgresql+asyncpg://postgres:postgres@localhost:5432/ai_test_engineer`
- LLM Provider: Set LLM_PROVIDER in .env (gemini/groq/ollama)

## Technology Decisions (CTO-level)
- **PostgreSQL over SQLite/MongoDB**: Relational integrity, JSONB, async support, cascade deletes
- **SQLAlchemy over raw SQL**: Security (SQL injection prevention), maintainability, migration safety, DB portability
- **asyncpg**: 3x faster than sync drivers, matches FastAPI async architecture
- **Gemini 2.5 Flash**: Free tier (250 RPD), vision support for Phase 3
- **pgvector (future)**: Vector search inside PostgreSQL — no separate DB needed
- **Redis (future)**: Cache (100x faster reads) + Celery task queue (background jobs)
- **Kafka (future, at scale)**: Only when 100+ concurrent users

## Rules
- Always use async/await for database operations
- Follow the existing 7-layer architecture — don't bypass layers
- Use Pydantic schemas for all API input/output
- Use the repository pattern for all database queries
- Keep LLM provider logic inside `app/ai/` only
- File type validation must happen in service layer
- Never hardcode secrets — use settings from config.py
- LLM responses must be parsed with llm_client.parse_json_response() for robustness
