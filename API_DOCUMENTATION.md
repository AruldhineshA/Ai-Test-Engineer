# AI Test Engineer Agent - API Documentation

## Project Progress Summary

### What We've Built So Far

| Layer | Component | Status |
|-------|-----------|--------|
| Entry Point | `app/main.py` - FastAPI app with CORS, lifespan events | DONE |
| API Routes | Projects, Documents, Test Cases endpoints | DONE |
| API Routes | Scripts endpoints | SKELETON (Phase 2) |
| Schemas | Pydantic validation for all request/response | DONE |
| Services | ProjectService, DocumentService, TestCaseService | DONE |
| Services | ScriptService | NOT CREATED |
| AI Engine | LLM Client (Gemini / Groq / Ollama) | DONE |
| AI Engine | Document Analyzer (PDF/DOCX/MD/TXT) | DONE |
| AI Engine | Test Case Generator | DONE |
| AI Engine | Script Generator | SKELETON (Phase 2) |
| Models | Project, Document, TestCase, Script DB models | DONE |
| Repositories | DocumentRepo, TestCaseRepo, ScriptRepo | DONE |
| Database | PostgreSQL + Alembic migration | CREATED (not run yet) |
| Config | `.env` with Gemini + Groq API keys | DONE |
| API Keys | Gemini 2.5 Flash - VERIFIED WORKING | DONE |
| API Keys | Groq Llama 3.3 70B - VERIFIED WORKING | DONE |

---

## Base URL

```
http://localhost:8000
```

## Swagger Docs (Auto-generated)

```
http://localhost:8000/docs
```

---

## All API Endpoints

### 1. Health Check

| Field | Value |
|-------|-------|
| **Method** | `GET` |
| **URL** | `/health` |
| **Status** | IMPLEMENTED |
| **Description** | Check if server is running |

**Response:**
```json
{
  "status": "healthy",
  "app": "AI Test Engineer Agent",
  "version": "1.0.0"
}
```

---

### 2. Projects

#### 2.1 Create Project

| Field | Value |
|-------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/projects/` |
| **Status** | IMPLEMENTED |
| **Description** | Create a new testing project |

**Request Body:**
```json
{
  "name": "Login Module Testing",
  "description": "Test cases for login feature"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Login Module Testing",
  "description": "Test cases for login feature",
  "created_at": "2026-03-06T10:00:00",
  "updated_at": "2026-03-06T10:00:00"
}
```

---

#### 2.2 List Projects

| Field | Value |
|-------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/projects/` |
| **Status** | IMPLEMENTED |
| **Description** | List all projects with pagination |

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `skip` | int | 0 | Number of records to skip |
| `limit` | int | 20 | Max records to return |

**Example:** `GET /api/v1/projects/?skip=0&limit=10`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Login Module Testing",
    "description": "Test cases for login feature",
    "created_at": "2026-03-06T10:00:00",
    "updated_at": "2026-03-06T10:00:00"
  }
]
```

---

#### 2.3 Get Project by ID

| Field | Value |
|-------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/projects/{project_id}` |
| **Status** | IMPLEMENTED |
| **Description** | Get a single project by its ID |

**Example:** `GET /api/v1/projects/1`

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Login Module Testing",
  "description": "Test cases for login feature",
  "created_at": "2026-03-06T10:00:00",
  "updated_at": "2026-03-06T10:00:00"
}
```

**Error (404):**
```json
{
  "detail": "Project with id 99 not found"
}
```

---

### 3. Documents

#### 3.1 Upload Document

| Field | Value |
|-------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/documents/upload` |
| **Status** | IMPLEMENTED |
| **Description** | Upload a document (PDF, DOCX, MD, TXT) |

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `project_id` | int | Yes | Which project this document belongs to |

**Request:** `multipart/form-data` with file field

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload?project_id=1" \
  -F "file=@requirements.pdf"
```

**Response (201 Created):**
```json
{
  "id": 1,
  "project_id": 1,
  "filename": "requirements.pdf",
  "file_type": "pdf",
  "status": "uploaded",
  "created_at": "2026-03-06T10:01:00"
}
```

**Supported File Types:** PDF, DOCX, MD, TXT

---

#### 3.2 Get Document

| Field | Value |
|-------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/documents/{document_id}` |
| **Status** | IMPLEMENTED |
| **Description** | Get document details by ID |

**Example:** `GET /api/v1/documents/1`

**Response (200 OK):**
```json
{
  "id": 1,
  "project_id": 1,
  "filename": "requirements.pdf",
  "file_type": "pdf",
  "status": "uploaded",
  "created_at": "2026-03-06T10:01:00"
}
```

---

#### 3.3 Analyze Document (AI)

| Field | Value |
|-------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/documents/{document_id}/analyze` |
| **Status** | IMPLEMENTED |
| **Description** | AI analyzes the document - extracts requirements and functional flows |

**What happens internally:**
1. Reads the uploaded document text (PDF/DOCX/MD/TXT)
2. Sends text to LLM (Gemini/Groq/Ollama)
3. AI extracts requirements, sections, and functional flows
4. Updates document status to "analyzed"
5. Stores parsed content in database

**Example:** `POST /api/v1/documents/1/analyze`

**Response (200 OK):**
```json
{
  "document_id": 1,
  "status": "analyzed",
  "extracted_sections": ["Login Flow", "Signup Flow", "Password Reset"],
  "requirements_count": 15,
  "message": "Document analyzed successfully"
}
```

---

### 4. Test Cases

#### 4.1 Generate Test Cases (AI)

| Field | Value |
|-------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/testcases/generate` |
| **Status** | IMPLEMENTED |
| **Description** | AI generates structured test cases from an analyzed document |

**Prerequisite:** Document must be analyzed first (call `/documents/{id}/analyze`)

**Request Body:**
```json
{
  "document_id": 1,
  "include_positive": true,
  "include_negative": true,
  "include_edge": true
}
```

**What happens internally:**
1. Gets the analyzed document's parsed content
2. Sends to AI Test Case Generator
3. AI generates structured test cases (positive + negative + edge)
4. Saves all test cases to database
5. Returns generated test cases

**Response (200 OK):**
```json
{
  "document_id": 1,
  "total_generated": 8,
  "message": "Successfully generated 8 test cases from 'requirements.pdf'",
  "test_cases": [
    {
      "id": 1,
      "test_case_id": "TC-001",
      "scenario": "Verify successful login with valid credentials",
      "preconditions": "User is registered and on the login page",
      "test_steps": [
        {
          "step_number": 1,
          "action": "Enter valid email in email field",
          "expected": "Email is accepted"
        },
        {
          "step_number": 2,
          "action": "Enter valid password in password field",
          "expected": "Password is masked"
        },
        {
          "step_number": 3,
          "action": "Click Login button",
          "expected": "User is redirected to dashboard"
        }
      ],
      "expected_result": "User is logged in and redirected to dashboard",
      "case_type": "positive",
      "status": "draft",
      "document_id": 1,
      "project_id": 1,
      "created_at": "2026-03-06T10:02:00"
    }
  ]
}
```

---

#### 4.2 List Test Cases

| Field | Value |
|-------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/testcases/` |
| **Status** | IMPLEMENTED |
| **Description** | List test cases for a project with optional filters |

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `project_id` | int | Yes | Filter by project |
| `case_type` | string | No | Filter: `positive`, `negative`, `edge` |
| `status` | string | No | Filter: `draft`, `approved`, `rejected` |

**Examples:**
```
GET /api/v1/testcases/?project_id=1
GET /api/v1/testcases/?project_id=1&case_type=negative
GET /api/v1/testcases/?project_id=1&status=approved
GET /api/v1/testcases/?project_id=1&case_type=edge&status=draft
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "test_case_id": "TC-001",
    "scenario": "Verify successful login with valid credentials",
    "preconditions": "User is registered and on the login page",
    "test_steps": [...],
    "expected_result": "User is logged in and redirected to dashboard",
    "case_type": "positive",
    "status": "draft",
    "document_id": 1,
    "project_id": 1,
    "created_at": "2026-03-06T10:02:00"
  }
]
```

---

#### 4.3 Update Test Case (Approve / Reject / Edit)

| Field | Value |
|-------|-------|
| **Method** | `PUT` |
| **URL** | `/api/v1/testcases/{testcase_id}` |
| **Status** | IMPLEMENTED |
| **Description** | Update, approve, or reject a test case |

**Example:** `PUT /api/v1/testcases/1`

**Request Body (approve):**
```json
{
  "status": "approved"
}
```

**Request Body (edit scenario):**
```json
{
  "scenario": "Verify login fails with invalid password",
  "expected_result": "Error message is shown"
}
```

**Request Body (reject):**
```json
{
  "status": "rejected"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "test_case_id": "TC-001",
  "scenario": "Verify login fails with invalid password",
  "status": "approved",
  "..."
}
```

---

#### 4.4 Export Test Cases (CSV Download)

| Field | Value |
|-------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/testcases/export` |
| **Status** | IMPLEMENTED |
| **Description** | Download all test cases for a project as CSV file |

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `project_id` | int | Yes | Which project to export |
| `format` | string | No | `csv` (default) or `excel` |

**Example:** `GET /api/v1/testcases/export?project_id=1&format=csv`

**Response:** File download (`testcases_project_1.csv`)

**CSV Columns:**
```
Test Case ID | Scenario | Preconditions | Test Steps | Expected Result | Type | Status
```

---

### 5. Scripts (Phase 2 - NOT YET IMPLEMENTED)

#### 5.1 Generate Script

| Field | Value |
|-------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/scripts/generate` |
| **Status** | NOT IMPLEMENTED (returns 501) |
| **Description** | Convert an approved test case into Playwright/Artillery script |

**Request Body (planned):**
```json
{
  "test_case_id": 1,
  "script_type": "playwright",
  "language": "python"
}
```

**Planned Response:**
```json
{
  "id": 1,
  "test_case_id": 1,
  "script_type": "playwright",
  "language": "python",
  "code_content": "import asyncio\nfrom playwright.async_api import...",
  "status": "generated",
  "created_at": "2026-03-06T10:05:00"
}
```

---

#### 5.2 Get Script

| Field | Value |
|-------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/scripts/{script_id}` |
| **Status** | NOT IMPLEMENTED (returns 501) |
| **Description** | Get a generated script by ID |

---

## Complete Endpoint Summary

| # | Method | Endpoint | Status | Phase |
|---|--------|----------|--------|-------|
| 1 | `GET` | `/health` | WORKING | - |
| 2 | `POST` | `/api/v1/projects/` | WORKING | 1 |
| 3 | `GET` | `/api/v1/projects/` | WORKING | 1 |
| 4 | `GET` | `/api/v1/projects/{id}` | WORKING | 1 |
| 5 | `POST` | `/api/v1/documents/upload` | WORKING | 1 |
| 6 | `GET` | `/api/v1/documents/{id}` | WORKING | 1 |
| 7 | `POST` | `/api/v1/documents/{id}/analyze` | WORKING | 1 |
| 8 | `POST` | `/api/v1/testcases/generate` | WORKING | 1 |
| 9 | `GET` | `/api/v1/testcases/` | WORKING | 1 |
| 10 | `PUT` | `/api/v1/testcases/{id}` | WORKING | 1 |
| 11 | `GET` | `/api/v1/testcases/export` | WORKING | 1 |
| 12 | `POST` | `/api/v1/scripts/generate` | NOT IMPLEMENTED | 2 |
| 13 | `GET` | `/api/v1/scripts/{id}` | NOT IMPLEMENTED | 2 |

**Total: 11 working endpoints + 2 planned for Phase 2**

---

## Complete User Flow (How to Use)

```
Step 1: Create Project
   POST /api/v1/projects/
   {"name": "My App Testing"}
         |
         v
Step 2: Upload Document
   POST /api/v1/documents/upload?project_id=1
   (attach PDF/DOCX/MD/TXT file)
         |
         v
Step 3: Analyze Document (AI)
   POST /api/v1/documents/1/analyze
   (AI extracts requirements from document)
         |
         v
Step 4: Generate Test Cases (AI)
   POST /api/v1/testcases/generate
   {"document_id": 1, "include_positive": true, "include_negative": true, "include_edge": true}
   (AI generates structured test cases)
         |
         v
Step 5: Review & Approve/Reject
   GET  /api/v1/testcases/?project_id=1        (view all)
   PUT  /api/v1/testcases/1  {"status": "approved"}
   PUT  /api/v1/testcases/2  {"status": "rejected"}
         |
         v
Step 6: Export
   GET /api/v1/testcases/export?project_id=1&format=csv
   (downloads CSV file)
         |
         v
Step 7 (Phase 2 - TODO):
   POST /api/v1/scripts/generate
   {"test_case_id": 1, "script_type": "playwright", "language": "python"}
```

---

## What's Needed to Run

| Requirement | Status |
|-------------|--------|
| Python 3.11+ | Installed |
| Virtual environment (.venv) | Created |
| Dependencies (requirements.txt) | Installed |
| Gemini API Key | VERIFIED WORKING |
| Groq API Key | VERIFIED WORKING |
| PostgreSQL Database | NOT RUNNING (needed next) |
| Alembic Migration | CREATED (needs `alembic upgrade head`) |

**Next Step:** Set up PostgreSQL (via Docker or local install), then run the server and test all endpoints.
