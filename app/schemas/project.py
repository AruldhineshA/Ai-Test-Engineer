"""
Project Schemas
================
Pydantic models that define the SHAPE of data going in and out.

LEARN: Why separate Schemas from Database Models?
- Schema (Pydantic)  → Validates HTTP request/response data
- Model (SQLAlchemy) → Defines database table structure
- They look similar but serve different purposes
- You might not want to expose all DB columns in the API

NAMING CONVENTION:
- XxxCreate  → What the client sends to CREATE a resource
- XxxUpdate  → What the client sends to UPDATE a resource
- XxxResponse → What the API sends BACK to the client
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """What the client sends when creating a project."""
    name: str = Field(..., min_length=1, max_length=200, examples=["Login Module Testing"])
    description: str | None = Field(None, max_length=1000, examples=["Test cases for login feature"])


class ProjectResponse(BaseModel):
    """What the API returns for a project."""
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}  # Allows converting SQLAlchemy model → Pydantic


class ProjectList(BaseModel):
    """Paginated list of projects."""
    items: list[ProjectResponse]
    total: int
