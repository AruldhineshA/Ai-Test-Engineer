"""
Shared Dependencies
====================
Dependencies that are reused across multiple endpoints.

LEARN: Dependency Injection in FastAPI
- A "dependency" is a function that runs BEFORE your endpoint
- FastAPI calls it automatically when you use Depends()
- Common uses: DB sessions, auth checks, rate limiting

EXAMPLE:
    @router.get("/items")
    async def get_items(db: AsyncSession = Depends(get_db)):
        # 'db' is automatically created and passed by FastAPI
        # When this function ends, the session is closed
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates a database session for each request.

    HOW IT WORKS:
    1. Request comes in → new DB session created
    2. Your endpoint uses the session
    3. Request ends → session is automatically closed

    'yield' makes this a generator — FastAPI handles the lifecycle.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
