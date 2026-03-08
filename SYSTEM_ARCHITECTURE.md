# AI Test Engineer Agent - System Architecture & Project Structure

---

## 1. SYSTEM DIAGRAM (High-Level)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React/Next.js)                     │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌──────────────┐  │
│  │  Upload   │  │  Test Case   │  │  Script   │  │   Download   │  │
│  │  Document │  │  Viewer/Edit │  │  Viewer   │  │   Center     │  │
│  └─────┬─────┘  └──────┬───────┘  └─────┬─────┘  └──────┬───────┘  │
└────────┼───────────────┼────────────────┼───────────────┼───────────┘
         │               │                │               │
         ▼               ▼                ▼               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      API GATEWAY (FastAPI)                           │
│                    http://localhost:8000                             │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    FastAPI Router Layer                       │    │
│  │  /api/v1/documents   → Document Upload & Management          │    │
│  │  /api/v1/testcases   → Test Case Generation & CRUD           │    │
│  │  /api/v1/scripts     → Automation Script Generation          │    │
│  │  /api/v1/projects    → Project Management                    │    │
│  │  /api/v1/auth        → Authentication                        │    │
│  └─────────────┬───────────────────────────────┬───────────────┘    │
│                │                               │                    │
│  ┌─────────────▼─────────────┐   ┌─────────────▼─────────────┐     │
│  │    Service Layer           │   │    Background Tasks        │     │
│  │  ┌─────────────────────┐  │   │    (Celery + Redis)        │     │
│  │  │ DocumentService     │  │   │  ┌──────────────────────┐  │     │
│  │  │ TestCaseService     │  │   │  │ Long doc processing  │  │     │
│  │  │ ScriptGenService    │  │   │  │ Batch test gen       │  │     │
│  │  │ ProjectService      │  │   │  │ Script generation    │  │     │
│  │  └─────────┬───────────┘  │   │  └──────────────────────┘  │     │
│  └────────────┼──────────────┘   └─────────────────────────────┘    │
│               │                                                     │
│  ┌────────────▼──────────────────────────────────────────────┐      │
│  │                   AI Engine Layer                          │      │
│  │  ┌──────────────┐  ┌───────────────┐  ┌───────────────┐  │      │
│  │  │  Document     │  │  Test Case    │  │  Script       │  │      │
│  │  │  Analyzer     │  │  Generator    │  │  Generator    │  │      │
│  │  │  (LLM + RAG)  │  │  (LLM)       │  │  (LLM)       │  │      │
│  │  └──────┬────────┘  └──────┬────────┘  └──────┬────────┘  │      │
│  │         │                  │                   │          │      │
│  │  ┌──────▼──────────────────▼───────────────────▼────────┐ │      │
│  │  │           LLM Provider (OpenAI / Claude API)         │ │      │
│  │  └─────────────────────────────────────────────────────┘ │      │
│  └───────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
         │                                    │
         ▼                                    ▼
┌─────────────────────┐            ┌─────────────────────┐
│   PostgreSQL DB      │            │   File Storage      │
│  ┌───────────────┐  │            │  (Local / S3)       │
│  │ projects      │  │            │  ┌───────────────┐  │
│  │ documents     │  │            │  │ uploaded_docs  │  │
│  │ test_cases    │  │            │  │ generated_     │  │
│  │ scripts       │  │            │  │   scripts      │  │
│  │ users         │  │            │  │ exports        │  │
│  └───────────────┘  │            │  └───────────────┘  │
└─────────────────────┘            └─────────────────────┘
```

---

## 2. REQUEST FLOW DIAGRAM

```
   User uploads PRD document
            │
            ▼
   ┌──────────────────┐
   │  FastAPI Endpoint │  POST /api/v1/documents/upload
   │  (Validation)     │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  Document Service │  Save file + create DB record
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  Document Analyzer│  Extract text from PDF/DOCX/MD
   │  (AI Engine)      │  Parse into structured sections
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  Test Case Gen    │  Send parsed content to LLM
   │  (AI Engine)      │  Generate structured test cases
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  Save to Database │  Store test cases with metadata
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  Return Response  │  JSON response with test cases
   └──────────────────┘
```

---

## 3. PROJECT FOLDER STRUCTURE (Industry Standard)

```
D:\Ai-Test-Engineer\
│
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   ├── config.py                 # Settings & environment config
│   │
│   ├── api/                      # API layer (Routes/Endpoints)
│   │   ├── __init__.py
│   │   ├── deps.py               # Shared dependencies (DB session, auth)
│   │   └── v1/                   # API version 1
│   │       ├── __init__.py
│   │       ├── router.py         # Combines all v1 routers
│   │       ├── documents.py      # POST /upload, GET /documents
│   │       ├── testcases.py      # GET/POST/PUT test cases
│   │       ├── scripts.py        # POST generate, GET scripts
│   │       └── projects.py       # Project CRUD endpoints
│   │
│   ├── models/                   # Database models (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── base.py               # Base model class
│   │   ├── project.py            # Project model
│   │   ├── document.py           # Document model
│   │   ├── testcase.py           # TestCase model
│   │   └── script.py             # Script model
│   │
│   ├── schemas/                  # Pydantic schemas (Request/Response)
│   │   ├── __init__.py
│   │   ├── document.py           # DocumentCreate, DocumentResponse
│   │   ├── testcase.py           # TestCaseCreate, TestCaseResponse
│   │   ├── script.py             # ScriptCreate, ScriptResponse
│   │   └── project.py            # ProjectCreate, ProjectResponse
│   │
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── document_service.py   # Document processing logic
│   │   ├── testcase_service.py   # Test case generation logic
│   │   └── script_service.py     # Script generation logic
│   │
│   ├── ai/                       # AI Engine (core intelligence)
│   │   ├── __init__.py
│   │   ├── llm_client.py         # LLM API wrapper (OpenAI/Claude)
│   │   ├── document_analyzer.py  # Extract & parse documents
│   │   ├── testcase_generator.py # Generate test cases via LLM
│   │   ├── script_generator.py   # Generate automation scripts
│   │   └── prompts/              # Prompt templates
│   │       ├── __init__.py
│   │       ├── testcase_prompts.py
│   │       └── script_prompts.py
│   │
│   ├── db/                       # Database layer
│   │   ├── __init__.py
│   │   ├── session.py            # DB session factory
│   │   └── repositories/        # Data access layer
│   │       ├── __init__.py
│   │       ├── document_repo.py
│   │       ├── testcase_repo.py
│   │       └── script_repo.py
│   │
│   ├── core/                     # Core utilities
│   │   ├── __init__.py
│   │   ├── security.py           # Auth helpers
│   │   ├── exceptions.py         # Custom exceptions
│   │   └── file_handler.py       # File upload/download helpers
│   │
│   └── workers/                  # Background task workers
│       ├── __init__.py
│       └── tasks.py              # Celery tasks
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Shared test fixtures
│   ├── test_api/
│   │   ├── test_documents.py
│   │   ├── test_testcases.py
│   │   └── test_scripts.py
│   └── test_services/
│       ├── test_document_service.py
│       └── test_testcase_service.py
│
├── alembic/                      # Database migrations
│   ├── env.py
│   ├── versions/                 # Migration files
│   └── alembic.ini
│
├── uploads/                      # Uploaded documents storage
├── exports/                      # Generated exports storage
│
├── .env                          # Environment variables (NEVER commit)
├── .env.example                  # Example env file (commit this)
├── .gitignore
├── requirements.txt              # Python dependencies
├── pyproject.toml                # Project metadata
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 4. LAYER-BY-LAYER EXPLANATION (Learn FastAPI Through This)

### Layer 1: `main.py` — The Entry Point
```
What it does:  Creates the FastAPI app, adds middleware, includes routers
Think of it:   The "main gate" of your application
You'll learn:  App initialization, CORS, lifespan events
```

### Layer 2: `api/v1/` — Routes (Endpoints)
```
What it does:  Defines HTTP endpoints (GET, POST, PUT, DELETE)
Think of it:   The "receptionist" — receives requests, sends responses
You'll learn:  Path operations, request/response models, dependency injection
```

### Layer 3: `schemas/` — Pydantic Models
```
What it does:  Validates incoming data & shapes outgoing data
Think of it:   The "security guard" — checks if data is correct
You'll learn:  Pydantic validation, serialization, request/response contracts
```

### Layer 4: `services/` — Business Logic
```
What it does:  Contains the actual logic (generate test cases, process docs)
Think of it:   The "brain" — makes decisions, orchestrates work
You'll learn:  Service pattern, dependency injection, async programming
```

### Layer 5: `ai/` — AI Engine
```
What it does:  Talks to LLM APIs, manages prompts, processes AI responses
Think of it:   The "intelligence" — the AI core of your product
You'll learn:  LLM integration, prompt engineering, structured output parsing
```

### Layer 6: `models/` — Database Models
```
What it does:  Defines database table structures
Think of it:   The "filing cabinet" — how data is stored
You'll learn:  SQLAlchemy ORM, relationships, migrations
```

### Layer 7: `db/repositories/` — Data Access
```
What it does:  CRUD operations on the database
Think of it:   The "clerk" — reads/writes data from the filing cabinet
You'll learn:  Repository pattern, async DB queries, transactions
```

---

## 5. TECHNOLOGY STACK (Final)

| Component          | Technology              | Why                                    |
|--------------------|-------------------------|----------------------------------------|
| Backend Framework  | **FastAPI**             | Async, fast, auto-docs, type-safe      |
| Language           | **Python 3.11+**        | AI ecosystem, mature libraries         |
| Database           | **PostgreSQL**          | Production-grade, JSON support          |
| ORM                | **SQLAlchemy 2.0**      | Async support, industry standard        |
| Migrations         | **Alembic**             | DB schema version control               |
| Validation         | **Pydantic v2**         | Built into FastAPI, fast validation     |
| AI/LLM             | **OpenAI / Claude API** | Test case & script generation           |
| Doc Parsing        | **PyMuPDF + python-docx** | PDF & DOCX text extraction           |
| Background Tasks   | **Celery + Redis**      | Long-running AI tasks                   |
| Auth               | **JWT (python-jose)**   | Stateless authentication                |
| Testing            | **pytest + httpx**      | Async test support for FastAPI          |
| Containerization   | **Docker**              | Consistent deployment                   |
| API Docs           | **Swagger (auto)**      | FastAPI generates this automatically    |

---

## 6. DATABASE SCHEMA

```
┌─────────────────┐       ┌──────────────────────┐
│    projects      │       │     documents         │
├─────────────────┤       ├──────────────────────┤
│ id (PK)         │───┐   │ id (PK)              │
│ name            │   │   │ project_id (FK) ─────│──┐
│ description     │   │   │ filename             │  │
│ created_at      │   │   │ file_path            │  │
│ updated_at      │   │   │ file_type            │  │
└─────────────────┘   │   │ parsed_content       │  │
                      │   │ status               │  │
                      │   │ created_at           │  │
                      │   └──────────────────────┘  │
                      │                             │
                      │   ┌──────────────────────┐  │
                      │   │    test_cases         │  │
                      │   ├──────────────────────┤  │
                      │   │ id (PK)              │  │
                      └──▶│ project_id (FK)      │  │
                          │ document_id (FK) ────│──┘
                          │ test_case_id (str)   │
                          │ scenario             │
                          │ preconditions        │
                          │ test_steps (JSON)    │
                          │ expected_result      │
                          │ case_type            │  ← positive/negative/edge
                          │ status               │  ← draft/approved/rejected
                          │ created_at           │
                          └──────────┬───────────┘
                                     │
                          ┌──────────▼───────────┐
                          │    scripts            │
                          ├──────────────────────┤
                          │ id (PK)              │
                          │ test_case_id (FK)    │
                          │ script_type          │  ← playwright/artillery
                          │ language             │  ← python/javascript
                          │ code_content         │
                          │ status               │
                          │ created_at           │
                          └──────────────────────┘
```

---

## 7. API ENDPOINTS (Phase 1)

| Method | Endpoint                              | Description                    |
|--------|---------------------------------------|--------------------------------|
| POST   | `/api/v1/projects/`                   | Create a new project           |
| GET    | `/api/v1/projects/`                   | List all projects              |
| GET    | `/api/v1/projects/{id}`               | Get project details            |
| POST   | `/api/v1/documents/upload`            | Upload a document              |
| GET    | `/api/v1/documents/{id}`              | Get document details           |
| POST   | `/api/v1/documents/{id}/analyze`      | Trigger AI analysis            |
| POST   | `/api/v1/testcases/generate`          | Generate test cases from doc   |
| GET    | `/api/v1/testcases/?project_id=X`     | List test cases for project    |
| PUT    | `/api/v1/testcases/{id}`              | Update/approve test case       |
| GET    | `/api/v1/testcases/export?format=csv` | Export test cases              |

---
![alt text](image.png)
## 8. DEVELOPMENT ORDER (Step-by-Step Build Plan)

### Step 1: Project Setup & Config
- [ ] Initialize FastAPI project
- [ ] Setup virtual environment & install dependencies
- [ ] Create config.py with Pydantic Settings
- [ ] Create main.py with app initialization

### Step 2: Database Setup
- [ ] Setup PostgreSQL connection
- [ ] Create SQLAlchemy models
- [ ] Setup Alembic migrations
- [ ] Run first migration

### Step 3: API Skeleton
- [ ] Create all router files with empty endpoints
- [ ] Create Pydantic schemas
- [ ] Verify Swagger docs at /docs

### Step 4: Document Upload Feature
- [ ] File upload endpoint
- [ ] File validation (PDF, DOCX, MD)
- [ ] Save to disk + database record

### Step 5: AI Document Analyzer
- [ ] PDF/DOCX text extraction
- [ ] LLM integration (OpenAI/Claude)
- [ ] Parse document into structured sections

### Step 6: Test Case Generation
- [ ] Prompt engineering for test case generation
- [ ] LLM call to generate test cases
- [ ] Parse & save structured test cases
- [ ] Export to CSV/Excel

### Step 7: Testing & Polish
- [ ] Write API tests with pytest
- [ ] Error handling & validation
- [ ] Logging setup
- [ ] Docker setup

---

## 9. KEY FASTAPI CONCEPTS YOU'LL LEARN

| Concept                  | Where in Project             | What it Does                        |
|--------------------------|------------------------------|-------------------------------------|
| Path Operations          | `api/v1/*.py`                | Define HTTP endpoints               |
| Dependency Injection     | `api/deps.py`               | Share DB sessions, auth across routes|
| Pydantic Models          | `schemas/*.py`               | Validate & serialize data           |
| Background Tasks         | `workers/tasks.py`           | Run long AI tasks in background     |
| Middleware               | `main.py`                    | CORS, logging, error handling       |
| Async/Await              | Everywhere                   | Non-blocking I/O operations         |
| File Upload              | `api/v1/documents.py`        | Handle multipart file uploads       |
| Error Handling           | `core/exceptions.py`         | Custom HTTP exceptions              |
| Settings Management      | `config.py`                  | Environment-based configuration     |
| Auto Documentation       | `/docs` endpoint             | Swagger UI (comes free!)            |
