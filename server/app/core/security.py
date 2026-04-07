"""
Security Utilities
===================
JWT token creation/verification and password hashing.

HOW JWT AUTH WORKS:
1. User sends email + password to /auth/login
2. Server verifies password, creates a JWT token
3. Server returns token to client
4. Client sends token in every request: Authorization: Bearer <token>
5. Server verifies token before processing the request
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Password hashing setup (bcrypt algorithm)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if a plain password matches the hashed version."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, email: str) -> str:
    """
    Create a JWT token containing user info.

    The token contains:
    - sub: user ID (subject)
    - email: user's email
    - exp: expiration time
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> dict | None:
    """
    Decode and verify a JWT token.
    Returns the payload if valid, None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
