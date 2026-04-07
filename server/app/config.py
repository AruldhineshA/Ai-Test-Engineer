"""
Application Configuration
=========================
Uses Pydantic BaseSettings to load config from .env file.
All settings are centralized here — never hardcode secrets in code.

HOW IT WORKS:
- Pydantic reads from .env file automatically
- You access settings like: settings.DATABASE_URL
- Type validation happens automatically (str, int, bool)
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Base directory of the project (D:\Ai-Test-Engineer)
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    All application settings in one place.
    Values are loaded from .env file → environment variables → defaults.
    """

    # ── App Settings ──────────────────────────────────────────────
    APP_NAME: str = "AI Test Engineer Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # ── Database ──────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_test_engineer"

    # ── LLM Provider Settings ────────────────────────────────────
    # Options: "gemini", "groq", "ollama"
    LLM_PROVIDER: str = "gemini"

    # Gemini (Free tier - ~10 RPM, ~250 RPD)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Groq (Free tier - 30 RPM)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Ollama (Local - unlimited)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"

    # ── File Storage ─────────────────────────────────────────────
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    EXPORT_DIR: str = str(BASE_DIR / "exports")
    MAX_UPLOAD_SIZE_MB: int = 20

    # ── CORS (Frontend Access) ───────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # ── Security ─────────────────────────────────────────────────
    SECRET_KEY: str = "change-this-to-a-random-secret-key-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Single instance used across the app
# Import this wherever you need settings: from app.config import settings
settings = Settings()
