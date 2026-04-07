"""
Test Case Schemas
==================
Defines data shapes for test case generation, display, and updates.
This is the CORE schema of Phase 1.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class CaseType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    EDGE = "edge"


class TestCaseStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"


class TestStep(BaseModel):
    """A single step in a test case."""
    step_number: int
    action: str = Field(..., examples=["Click the Login button"])
    expected: str = Field(..., examples=["Login form appears"])


class TestCaseGenerateRequest(BaseModel):
    """Request body to generate test cases from a document."""
    document_id: int
    include_positive: bool = Field(True, description="Generate positive test cases")
    include_negative: bool = Field(True, description="Generate negative test cases")
    include_edge: bool = Field(True, description="Generate edge case test cases")


class TestCaseGenerateResponse(BaseModel):
    """Response after generating test cases."""
    document_id: int
    total_generated: int
    test_cases: list["TestCaseResponse"]
    message: str


class TestCaseResponse(BaseModel):
    """What the API returns for a single test case."""
    id: int
    test_case_id: str = Field(..., examples=["TC-001"])
    scenario: str = Field(..., examples=["Verify successful login with valid credentials"])
    preconditions: str = Field(..., examples=["User is registered and on the login page"])
    test_steps: list[TestStep]
    expected_result: str = Field(..., examples=["User is redirected to dashboard"])
    case_type: CaseType
    status: TestCaseStatus
    document_id: int
    project_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TestCaseUpdate(BaseModel):
    """Fields that can be updated on a test case."""
    scenario: str | None = None
    preconditions: str | None = None
    test_steps: list[TestStep] | None = None
    expected_result: str | None = None
    status: TestCaseStatus | None = None
