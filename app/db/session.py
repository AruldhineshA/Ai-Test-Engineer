"""
Database Session Factory
=========================
Creates async database connections.

LEARN: Async Database Access
- "async" means non-blocking — your app can handle other requests
  while waiting for the database to respond
- AsyncSession is the async version of SQLAlchemy Session
- We use a "factory" pattern to create sessions on demand
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# Engine: The connection to the database
# echo=True logs all SQL queries (helpful for learning, disable in production)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Session Factory: Creates new sessions when called
# Each API request gets its own session (via deps.py)
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
