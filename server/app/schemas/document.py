"""
Document Schemas
=================
Defines data shapes for document upload and analysis.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    """
    LEARN: str + Enum = String enum
    - Values are stored as strings in DB
    - FastAPI validates that only these values are accepted
    """
    UPLOADED = "uploaded"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    FAILED = "failed"


class DocumentResponse(BaseModel):
    """What the API returns for a document."""
    id: int
    project_id: int
    filename: str
    file_type: str
    status: DocumentStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentAnalyzeResponse(BaseModel):
    """What the API returns after analyzing a document."""
    document_id: int
    status: DocumentStatus
    extracted_sections: list[str] = Field(
        default_factory=list,
        description="List of functional sections found in the document",
    )
    requirements_count: int = Field(0, description="Number of requirements extracted")
    message: str = Field("", description="Status message")
