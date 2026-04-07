"""
Shared Dependencies
====================
Dependencies that are reused across multiple endpoints.

LEARN: Dependency Injection in FastAPI
- A "dependency" is a function that runs BEFORE your endpoint
- FastAPI calls it automatically when you use Depends()
- Common uses: DB sessions, auth checks, rate limiting
"""

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.core.security import verify_access_token
from app.models.user import User
from app.services.auth_service import AuthService

# Bearer token scheme — extracts token from "Authorization: Bearer <token>" header
bearer_scheme = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates a database session for each request.

    HOW IT WORKS:
    1. Request comes in → new DB session created
    2. Your endpoint uses the session
    3. Request ends → session is automatically closed
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extracts and verifies JWT token from request header.
    Returns the authenticated User object.

    HOW IT WORKS:
    1. Client sends: Authorization: Bearer eyJhbGciOi...
    2. HTTPBearer extracts the token
    3. We verify and decode the JWT
    4. We fetch the user from database
    5. Return the user (or raise 401)
    """
    payload = verify_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload["sub"])
    service = AuthService(db)
    user = await service.get_user_by_id(user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user
