# AI Test Engineer - Study Notes & Commands Reference

> **For:** Developers coming from Flask/Django who are new to FastAPI + PostgreSQL + async Python
> **Project:** AI-powered test case generator from documents

---

## Table of Contents
1. [How FastAPI Differs from Flask/Django](#1-fastapi-vs-flaskdjango---what-you-already-know)
2. [PostgreSQL Essentials](#2-postgresql-essentials)
3. [SQLAlchemy 2.0 Async (Our ORM)](#3-sqlalchemy-20-async-our-orm)
4. [Alembic Migrations](#4-alembic-migrations)
5. [How AI Models Are Used](#5-how-ai-models-are-used-in-this-project)
6. [Full Request Flow Explained](#6-full-request-flow-explained)
7. [Project Commands Cheatsheet](#7-project-commands-cheatsheet)
8. [PostgreSQL Query Reference](#8-postgresql-query-reference)
9. [Docker Commands](#9-docker-commands)
10. [Debugging Tips](#10-debugging-tips)

---

## 1. FastAPI vs Flask/Django - What You Already Know

| Concept | Flask | Django | FastAPI (Our Project) |
|---------|-------|--------|----------------------|
| App creation | `app = Flask(__name__)` | `django-admin startproject` | `app = FastAPI()` |
| Routes | `@app.route("/")` | `urls.py` | `@router.get("/")` |
| Request data | `request.form` / `request.json` | `request.POST` | **Pydantic schema** (auto-validated!) |
| Response | `jsonify({})` | `JsonResponse({})` | Just `return {}` (auto-converted) |
| ORM | SQLAlchemy (sync) | Django ORM | SQLAlchemy 2.0 (**async**) |
| Migrations | Flask-Migrate (Alembic) | `manage.py migrate` | Alembic directly |
| Auth | Flask-Login | Django auth | **JWT tokens** (manual) |
| Async | Not native | Limited | **Native async/await** |
| Docs | Swagger (manual) | None built-in | **Auto Swagger** at `/docs` |

### Key Difference: async/await
```python
# Flask (sync) - blocks the thread while waiting for DB
@app.route("/users")
def get_users():
    users = db.session.query(User).all()  # Thread BLOCKED here
    return jsonify(users)

# FastAPI (async) - thread is FREE while waiting for DB
@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))  # Thread FREE to handle other requests
    return result.scalars().all()
```

**Why async matters:** If 100 users hit your API at once:
- Flask: Needs 100 threads (expensive, uses lots of memory)
- FastAPI: 1 thread handles all 100 (while one waits for DB, it serves others)

### Key Difference: Pydantic Validation (replaces Flask-WTF / Django Forms)
```python
# Flask - you manually validate
@app.route("/projects", methods=["POST"])
def create_project():
    data = request.json
    if not data.get("name"):          # Manual validation
        return {"error": "name required"}, 400
    # ... more manual checks

# FastAPI - Pydantic auto-validates BEFORE your code runs
class ProjectCreate(BaseModel):
    name: str                          # Required string
    description: str | None = None     # Optional string

@router.post("/projects/")
async def create_project(project: ProjectCreate):  # Auto-validated!
    # If name is missing, FastAPI returns 422 automatically
    # You never see invalid data
    pass
```

### Key Difference: Dependency Injection
```python
# Flask - you import db directly or use g
from app import db
@app.route("/data")
def get_data():
    db.session.query(...)

# FastAPI - dependencies are INJECTED into your function
@router.get("/data")
async def get_data(
    db: AsyncSession = Depends(get_db),         # DB session injected
    user: User = Depends(get_current_user),      # Auth user injected
):
    # db and user are ready to use
    # FastAPI handles creating/closing db session automatically
    pass
```

Think of `Depends()` like Django middleware, but for individual routes.

---

## 2. PostgreSQL Essentials

### What is PostgreSQL?
- **Relational database** like MySQL but more powerful
- Supports **JSONB** (store JSON data with indexing - we use this for test_steps)
- Supports **async connections** via asyncpg driver
- Has **CASCADE deletes** (delete project = auto-delete its documents + test cases)

### Install & Setup (Windows)
```bash
# Option 1: Install directly
# Download from https://www.postgresql.org/download/windows/
# Default port: 5432, default user: postgres

# Option 2: Use Docker (recommended - what we do)
docker-compose up db    # Starts PostgreSQL in a container
```

### Connect to PostgreSQL
```bash
# Using psql (PostgreSQL CLI)
psql -U postgres -h localhost -p 5432 -d ai_test_engineer

# Using Docker
docker exec -it ai-test-engineer-db-1 psql -U postgres -d ai_test_engineer

# Connection URL format (what our app uses):
# postgresql+asyncpg://username:password@host:port/database_name
# postgresql+asyncpg://postgres:postgres@localhost:5432/ai_test_engineer
```

### PostgreSQL vs SQLite (what you might know)
| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| Setup | Zero (file-based) | Needs server |
| Concurrent writes | One at a time | Many at once |
| JSON support | Basic | **JSONB** (indexed, queryable) |
| Async support | No | Yes (asyncpg) |
| Production ready | No (for web apps) | Yes |
| Max DB size | ~281 TB | Unlimited |

---

## 3. SQLAlchemy 2.0 Async (Our ORM)

### Django ORM vs SQLAlchemy - Quick Comparison
```python
# Django ORM
class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

# SQLAlchemy 2.0 (our project)
class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
```

### How Our Models Connect (Relationships)
```
User (1) ──────< Project (many)
                    │
                    ├──< Document (many)
                    │        │
                    │        └──< TestCase (many)
                    │                  │
                    └──< TestCase      └──< Script (many) [Phase 2]
```

```python
# In Project model - "one project has many documents"
class Project(Base):
    documents: Mapped[list["Document"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan"    # Delete project = delete all its documents
    )

# In Document model - "one document belongs to one project"
class Document(Base):
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="documents")
```

### Async Database Operations
```python
# CREATE - Insert new record
async def create(self, document: Document) -> Document:
    self.db.add(document)                # Stage for insert
    await self.db.flush()                # Send INSERT to database
    await self.db.refresh(document)      # Get auto-generated id, created_at
    return document

# READ - Get by ID
async def get_by_id(self, doc_id: int) -> Document | None:
    result = await self.db.execute(
        select(Document).where(Document.id == doc_id)
    )
    return result.scalar_one_or_none()

# READ - Get with filters
async def get_by_project(self, project_id: int, case_type: str = None):
    query = select(TestCase).where(TestCase.project_id == project_id)
    if case_type:
        query = query.where(TestCase.case_type == case_type)
    result = await self.db.execute(query)
    return result.scalars().all()

# UPDATE
async def update(self, tc_id: int, data: dict) -> TestCase:
    tc = await self.get_by_id(tc_id)
    for key, value in data.items():
        setattr(tc, key, value)          # tc.status = "approved"
    await self.db.flush()
    await self.db.refresh(tc)
    return tc

# BULK INSERT
async def create_many(self, testcases: list[TestCase]) -> list[TestCase]:
    self.db.add_all(testcases)           # Stage all for insert
    await self.db.flush()                # Send all INSERTs at once
    for tc in testcases:
        await self.db.refresh(tc)        # Get generated IDs
    return testcases
```

### Important: flush() vs commit()
```python
# flush() = Send SQL to database but DON'T finalize (can still rollback)
await db.flush()

# commit() = Finalize all changes (permanent)
await db.commit()

# In our project, commit happens automatically in the dependency:
async def get_db():
    async with async_session() as session:
        try:
            yield session          # Route uses the session
            await session.commit() # Auto-commit if no errors
        except:
            await session.rollback()  # Auto-rollback on error
            raise
```

---

## 4. Alembic Migrations

### What is Alembic?
Like Django's `manage.py makemigrations` + `manage.py migrate`, but manual.

| Django | Alembic (Our Project) |
|--------|----------------------|
| `python manage.py makemigrations` | `alembic revision --autogenerate -m "message"` |
| `python manage.py migrate` | `alembic upgrade head` |
| `python manage.py showmigrations` | `alembic history` |
| `python manage.py migrate app 0001` | `alembic downgrade <revision>` |

### Our Migrations
```
server/alembic/versions/
├── 001_initial_schema.py      → Creates: projects, documents, test_cases, scripts
└── 002_add_users_table.py     → Creates: users table, adds user_id to projects
```

### Migration Commands
```bash
cd server

# Apply all migrations (create tables)
alembic upgrade head

# See current migration status
alembic current

# See migration history
alembic history --verbose

# Create new migration after changing models
alembic revision --autogenerate -m "add_new_table"

# Rollback last migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback everything (destroy all tables)
alembic downgrade base
```

---

## 5. How AI Models Are Used in This Project

### Architecture: Strategy Pattern
```
                    ┌─────────────────┐
                    │   LLM Client    │  ← Single interface
                    │  generate()     │
                    │  parse_json()   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
    ┌─────────▼──┐  ┌───────▼────┐  ┌──────▼─────┐
    │   Gemini   │  │    Groq    │  │   Ollama   │
    │  2.5 Flash │  │  Llama 3.3 │  │  (local)   │
    │  (Google)  │  │   70B      │  │            │
    └────────────┘  └────────────┘  └────────────┘
```

**Switch provider** by changing `LLM_PROVIDER` in `.env`:
```env
LLM_PROVIDER=gemini       # Google Gemini 2.5 Flash (free, 250 req/day)
# LLM_PROVIDER=groq       # Groq Llama 3.3 70B (free, 30 req/min)
# LLM_PROVIDER=ollama     # Local model (unlimited, needs GPU)
```

### How AI Analysis Works (Step by Step)

**Step 1: Extract text from document**
```python
# document_analyzer.py
async def extract_text(file_path: str, file_type: str) -> str:
    if file_type == "pdf":
        doc = fitz.open(file_path)           # PyMuPDF opens PDF
        text = ""
        for page in doc:
            text += page.get_text()          # Extract text from each page
        return text
    elif file_type == "docx":
        doc = DocxDocument(file_path)        # python-docx opens DOCX
        text = "\n".join([p.text for p in doc.paragraphs])
        return text
    # ... md and txt are just file reads
```

**Step 2: AI analyzes the text**
```python
# document_analyzer.py
async def analyze(text: str) -> dict:
    text = text[:30000]  # Truncate to fit LLM token limit

    prompt = f"""Analyze this document and extract:
    1. Sections/headings
    2. Functional requirements
    3. Non-functional requirements
    4. User flows

    Document text:
    {text}

    Return as JSON..."""

    response = await self.llm_client.generate(prompt, system_prompt)
    parsed = self.llm_client.parse_json_response(response)
    # Returns: {sections: [...], requirements: [...], functional_flows: [...]}
    return parsed
```

**Step 3: AI generates test cases**
```python
# testcase_generator.py
async def generate(parsed_content: dict, include_positive=True, ...) -> list:
    prompt = f"""Based on this analysis, generate test cases:

    Analysis: {parsed_content}

    Generate: positive, negative, edge case tests

    Return JSON array:
    [{{
        "test_case_id": "TC-001",
        "scenario": "Verify login with valid credentials",
        "preconditions": "User account exists",
        "test_steps": [
            {{"step_number": 1, "action": "Navigate to login", "expected": "Login page loads"}},
            {{"step_number": 2, "action": "Enter credentials", "expected": "Fields accept input"}}
        ],
        "expected_result": "User logged in successfully",
        "case_type": "positive"
    }}]"""

    response = await self.llm_client.generate(prompt, system_prompt)
    test_cases = self.llm_client.parse_json_response(response)
    return validated_test_cases
```

### JSON Response Parsing (Important!)
LLMs sometimes return JSON wrapped in markdown. Our parser handles this:
```python
def parse_json_response(self, response_text: str) -> dict | list:
    # LLM might return:
    # ```json
    # {"key": "value"}
    # ```

    # Step 1: Try direct JSON parse
    # Step 2: If fails, strip markdown code blocks
    # Step 3: Try again
    # This is why we always use parse_json_response() instead of json.loads()
```

---

## 6. Full Request Flow Explained

### The 7-Layer Journey (for every API request)

```
Browser/Postman
    │
    ▼
[Layer 1] main.py ──── FastAPI app receives request
    │                   CORS middleware checks origin
    │                   Routes to correct endpoint
    ▼
[Layer 2] api/v1/ ──── Route handler function
    │                   Depends(get_db) → gets database session
    │                   Depends(get_current_user) → validates JWT token
    │                   Receives auto-validated Pydantic schema
    ▼
[Layer 3] schemas/ ──── Pydantic validates input BEFORE your code runs
    │                    Wrong type? → 422 error automatically
    │                    Missing required field? → 422 error automatically
    ▼
[Layer 4] services/ ── Business logic layer
    │                   Orchestrates operations
    │                   Calls AI engine if needed
    │                   Calls repository for database ops
    ▼
[Layer 5] ai/ ──────── AI engine (only for analyze/generate)
    │                   Sends prompts to LLM
    │                   Parses JSON response
    │                   Validates AI output
    ▼
[Layer 6] models/ ──── SQLAlchemy models define table structure
    │                   Relationships between tables
    │                   Column types and constraints
    ▼
[Layer 7] db/repos/ ── Repository executes actual SQL
                        select(), insert(), update()
                        Returns model instances
```

### Example: "Generate Test Cases" - Complete Flow
```
POST /api/v1/testcases/generate
Body: {"document_id": 5, "include_positive": true, "include_negative": true}

1. FastAPI receives request
2. get_db() creates AsyncSession (database connection)
3. get_current_user() verifies JWT token from Authorization header
4. Pydantic validates body → TestCaseGenerateRequest
5. testcases.py route calls TestCaseService.generate()
6. Service gets Document from DB via DocumentRepository
7. Service checks document.status == "analyzed"
8. Service calls TestCaseGenerator.generate(document.parsed_content)
9. TestCaseGenerator builds prompt from template
10. LLMClient.generate() sends prompt to Gemini API
11. Gemini returns JSON string with test cases
12. LLMClient.parse_json_response() extracts clean JSON
13. TestCaseGenerator validates each test case
14. Service creates TestCase model instances
15. TestCaseRepository.create_many() bulk inserts to PostgreSQL
16. Service returns TestCaseGenerateResponse
17. FastAPI serializes to JSON and sends response
18. get_db() auto-commits the transaction
```

---

## 7. Project Commands Cheatsheet

### Server (Backend)
```bash
# Navigate to server
cd server

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from example)
cp .env.example .env
# Then edit .env with your API keys

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_api/test_health.py -v

# Lint code
ruff check app/

# Auto-fix lint issues
ruff check app/ --fix

# Format code
ruff format app/
```

### Client (Frontend)
```bash
# Navigate to client
cd client

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Docker
```bash
# Start everything (server + client + database)
docker-compose up

# Start in background
docker-compose up -d

# Start only database
docker-compose up db

# Stop everything
docker-compose down

# Stop and remove volumes (DELETES database data!)
docker-compose down -v

# Rebuild after code changes
docker-compose up --build

# View logs
docker-compose logs -f server
docker-compose logs -f db

# Enter database container
docker exec -it ai-test-engineer-db-1 psql -U postgres -d ai_test_engineer
```

### Git
```bash
git status
git add .
git commit -m "your message"
git push origin main
git log --oneline -10
```

---

## 8. PostgreSQL Query Reference

### Connect First
```bash
# Via Docker
docker exec -it ai-test-engineer-db-1 psql -U postgres -d ai_test_engineer

# Direct (if PostgreSQL installed locally)
psql -U postgres -h localhost -p 5432 -d ai_test_engineer
```

### Database Management
```sql
-- List all databases
\l

-- Connect to our database
\c ai_test_engineer

-- List all tables
\dt

-- Describe a table (see columns, types)
\d projects
\d documents
\d test_cases
\d users

-- Show table with all details
\d+ test_cases

-- Quit psql
\q
```

### Basic CRUD Queries
```sql
-- ===== USERS =====
-- See all users
SELECT id, email, full_name, is_active, created_at FROM users;

-- Find user by email
SELECT * FROM users WHERE email = 'john@example.com';

-- Count users
SELECT COUNT(*) FROM users;

-- ===== PROJECTS =====
-- See all projects
SELECT * FROM projects;

-- Projects with owner name
SELECT p.id, p.name, p.description, u.email as owner
FROM projects p
JOIN users u ON p.user_id = u.id;

-- Projects for a specific user
SELECT * FROM projects WHERE user_id = 1;

-- ===== DOCUMENTS =====
-- All documents with their project name
SELECT d.id, d.filename, d.file_type, d.status, p.name as project
FROM documents d
JOIN projects p ON d.project_id = p.id;

-- Documents that are analyzed (ready for test case generation)
SELECT id, filename, status FROM documents WHERE status = 'analyzed';

-- Documents that failed analysis
SELECT id, filename, status FROM documents WHERE status = 'failed';

-- ===== TEST CASES =====
-- All test cases for a project
SELECT id, test_case_id, scenario, case_type, status
FROM test_cases
WHERE project_id = 1
ORDER BY test_case_id;

-- Count test cases by type
SELECT case_type, COUNT(*) as total
FROM test_cases
WHERE project_id = 1
GROUP BY case_type;

-- Count test cases by status
SELECT status, COUNT(*) as total
FROM test_cases
WHERE project_id = 1
GROUP BY status;

-- Approved test cases only
SELECT test_case_id, scenario, expected_result
FROM test_cases
WHERE project_id = 1 AND status = 'approved';

-- View test steps (JSONB column)
SELECT test_case_id, scenario, test_steps
FROM test_cases
WHERE id = 1;

-- Pretty-print test steps
SELECT test_case_id, jsonb_pretty(test_steps::jsonb) as steps
FROM test_cases
WHERE id = 1;
```

### Advanced Queries
```sql
-- ===== JSONB QUERIES (test_steps column) =====

-- Find test cases with more than 5 steps
SELECT test_case_id, scenario, jsonb_array_length(test_steps::jsonb) as step_count
FROM test_cases
WHERE jsonb_array_length(test_steps::jsonb) > 5;

-- Search inside test steps for a keyword
SELECT test_case_id, scenario
FROM test_cases
WHERE test_steps::text ILIKE '%login%';

-- Get first step of each test case
SELECT test_case_id, test_steps::jsonb->0->>'action' as first_action
FROM test_cases;

-- ===== JOINS & AGGREGATIONS =====

-- Full project summary
SELECT
    p.name as project,
    COUNT(DISTINCT d.id) as documents,
    COUNT(DISTINCT tc.id) as test_cases,
    COUNT(DISTINCT CASE WHEN tc.status = 'approved' THEN tc.id END) as approved,
    COUNT(DISTINCT CASE WHEN tc.status = 'draft' THEN tc.id END) as draft
FROM projects p
LEFT JOIN documents d ON d.project_id = p.id
LEFT JOIN test_cases tc ON tc.project_id = p.id
GROUP BY p.id, p.name;

-- Documents with test case count
SELECT
    d.filename,
    d.status as doc_status,
    COUNT(tc.id) as test_cases_generated
FROM documents d
LEFT JOIN test_cases tc ON tc.document_id = d.id
GROUP BY d.id, d.filename, d.status;

-- ===== USEFUL ADMIN QUERIES =====

-- Database size
SELECT pg_size_pretty(pg_database_size('ai_test_engineer'));

-- Table sizes
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::text)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::text) DESC;

-- Recent test cases (last 24 hours)
SELECT test_case_id, scenario, created_at
FROM test_cases
WHERE created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;

-- Check foreign key relationships
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table,
    ccu.column_name AS foreign_column
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';

-- ===== DANGER ZONE (be careful!) =====

-- Delete all test cases for a project
-- DELETE FROM test_cases WHERE project_id = 1;

-- Delete a project (cascades to documents + test cases)
-- DELETE FROM projects WHERE id = 1;

-- Reset auto-increment
-- ALTER SEQUENCE test_cases_id_seq RESTART WITH 1;

-- Drop all tables (nuclear option)
-- DROP TABLE IF EXISTS scripts, test_cases, documents, projects, users CASCADE;
```

### PostgreSQL Data Types We Use
```sql
-- Our project uses these PostgreSQL types:
INTEGER         -- id, foreign keys (auto-increment via SERIAL)
VARCHAR(255)    -- short strings (name, email, filename)
TEXT            -- long strings (description, scenario, code_content)
JSONB           -- test_steps column (structured JSON, indexable)
BOOLEAN         -- is_active
TIMESTAMP       -- created_at, updated_at (auto-managed)
```

---

## 9. Docker Commands

### Our docker-compose.yml Services
| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `server` | Custom (FastAPI) | 8000 | Backend API |
| `client` | Custom (React) | 5173 | Frontend UI |
| `db` | postgres:16 | 5432 | PostgreSQL database |

```bash
# Start specific service
docker-compose up db              # Only database
docker-compose up server db       # Server + database (no frontend)
docker-compose up                 # Everything

# Useful Docker commands
docker ps                         # See running containers
docker-compose ps                 # See compose services
docker-compose exec server bash   # Shell into server container
docker-compose exec db psql -U postgres -d ai_test_engineer  # DB shell

# Troubleshooting
docker-compose logs server        # Server logs
docker-compose logs db            # Database logs
docker-compose restart server     # Restart server only
```

---

## 10. Debugging Tips

### Check if Database is Running
```bash
# Try connecting
docker-compose exec db pg_isready -U postgres
# Should output: "accepting connections"
```

### Check if Tables Exist
```sql
-- In psql:
\dt
-- Should show: users, projects, documents, test_cases, scripts
```

### Check Migration Status
```bash
cd server
alembic current     # Shows current migration revision
alembic history     # Shows all migrations
```

### Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Connection refused on port 5432` | PostgreSQL not running | `docker-compose up db` |
| `relation "projects" does not exist` | Migrations not run | `cd server && alembic upgrade head` |
| `UNIQUE constraint failed: users.email` | Duplicate email | Use different email |
| `Foreign key violation` | Referenced record doesn't exist | Create parent record first |
| `422 Unprocessable Entity` | Request body failed Pydantic validation | Check request format |
| `401 Unauthorized` | Missing/invalid JWT token | Login again, check Authorization header |
| `LLM rate limit` | Too many AI requests | Wait or switch provider in .env |

### Test API Endpoints (using curl or Postman)
```bash
# Health check
curl http://localhost:8000/health

# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com", "full_name":"Test User", "password":"test123"}'

# Login (save the token!)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com", "password":"test123"}'

# Create project (use token from login)
curl -X POST http://localhost:8000/api/v1/projects/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"name":"My Project", "description":"Testing project"}'

# Upload document
curl -X POST "http://localhost:8000/api/v1/documents/upload?project_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@requirements.pdf"

# Analyze document
curl -X POST http://localhost:8000/api/v1/documents/1/analyze \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Generate test cases
curl -X POST http://localhost:8000/api/v1/testcases/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"document_id":1, "include_positive":true, "include_negative":true, "include_edge":true}'

# Or just open http://localhost:8000/docs in browser for Swagger UI!
```

---

## Quick Reference: What Happens When

| User Action | Backend Flow |
|-------------|-------------|
| Register | API → AuthService → hash password → save User → return JWT |
| Login | API → AuthService → verify password → return JWT |
| Create Project | API → verify JWT → ProjectService → ProjectRepo → INSERT into projects |
| Upload Doc | API → verify JWT → DocService → validate file → save to disk → INSERT into documents |
| Analyze Doc | API → DocService → extract text (PyMuPDF/docx) → send to Gemini AI → save parsed_content |
| Generate Tests | API → TestCaseService → get parsed_content → send to Gemini AI → bulk INSERT test_cases |
| Export CSV | API → TestCaseService → SELECT test_cases → build CSV → StreamingResponse download |

---

> **Tip:** Open `http://localhost:8000/docs` after starting the server - FastAPI auto-generates interactive API documentation where you can test every endpoint!
