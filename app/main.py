"""
FastAPI Application Entry Point
================================
This is the "main gate" of the application.

WHAT HAPPENS HERE:
1. FastAPI app is created
2. CORS middleware is added (so frontend can talk to backend)
3. All API routers are included
4. Startup/shutdown events are handled

TO RUN:
    uvicorn app.main:app --reload

SWAGGER DOCS:
    Open http://localhost:8000/docs in your browser
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


# ── Lifespan: Runs on startup and shutdown ────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Code before 'yield' runs on STARTUP.
    Code after 'yield' runs on SHUTDOWN.
    """
    # STARTUP: Create upload/export directories if they don't exist
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.EXPORT_DIR).mkdir(parents=True, exist_ok=True)
    print(f"✓ {settings.APP_NAME} v{settings.APP_VERSION} started")
    print(f"✓ LLM Provider: {settings.LLM_PROVIDER}")
    print(f"✓ Docs available at: http://localhost:8000/docs")

    yield  # App is running and handling requests here

    # SHUTDOWN: Cleanup resources
    print(f"✗ {settings.APP_NAME} shutting down...")


# ── Create FastAPI App ────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered test case generation and automation script generator",
    lifespan=lifespan,
)


# ── CORS Middleware ───────────────────────────────────────────────
# This allows your React/Next.js frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# ── Include API Routers ──────────────────────────────────────────
from app.api.v1.router import api_v1_router  # noqa: E402

app.include_router(api_v1_router, prefix=settings.API_PREFIX)


# ── Health Check Endpoint ─────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    """Quick check to see if the server is running."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
