"""
Auth Service
=============
Business logic for user registration and login.
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import hash_password, verify_password, create_access_token

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: RegisterRequest) -> dict:
        """Register a new user."""
        # Check if email already exists
        existing = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        if existing.scalar_one_or_none():
            raise ValueError("Email already registered")

        # Create user with hashed password
        user = User(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        # Generate token
        token = create_access_token(user.id, user.email)
        logger.info(f"User registered: {user.email}")

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user,
        }

    async def login(self, data: LoginRequest) -> dict:
        """Authenticate user and return token."""
        result = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(data.password, user.hashed_password):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Account is deactivated")

        token = create_access_token(user.id, user.email)
        logger.info(f"User logged in: {user.email}")

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user,
        }

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
