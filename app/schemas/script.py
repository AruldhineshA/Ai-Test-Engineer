"""
Script Schemas (Phase 2)
=========================
Defines data shapes for automation script generation.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ScriptType(str, Enum):
    PLAYWRIGHT = "playwright"
    ARTILLERY = "artillery"


class ScriptLanguage(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"


class ScriptGenerateRequest(BaseModel):
    """Request to generate an automation script from a test case."""
    test_case_id: int
    script_type: ScriptType = Field(..., examples=["playwright"])
    language: ScriptLanguage = Field(ScriptLanguage.PYTHON, examples=["python"])


class ScriptResponse(BaseModel):
    """What the API returns for a generated script."""
    id: int
    test_case_id: int
    script_type: ScriptType
    language: ScriptLanguage
    code_content: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
