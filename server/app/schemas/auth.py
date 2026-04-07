"""
Auth Schemas
=============
Request/response models for authentication endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """What the client sends to register."""
    email: EmailStr = Field(..., examples=["user@example.com"])
    full_name: str = Field(..., min_length=2, max_length=200, examples=["Arul Dinesh"])
    password: str = Field(..., min_length=6, max_length=100, examples=["strongpassword123"])


class LoginRequest(BaseModel):
    """What the client sends to login."""
    email: EmailStr = Field(..., examples=["user@example.com"])
    password: str = Field(..., examples=["strongpassword123"])


class TokenResponse(BaseModel):
    """What the API returns after login."""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    """User info returned in API responses."""
    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
