"""
Test Case Endpoints
====================
Handles test case generation, listing, updating, and export.

LEARN:
- response_model: Tells FastAPI what shape the response will be
- Query parameters with defaults: Optional filters in the URL
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.testcase import (
    TestCaseResponse,
    TestCaseUpdate,
    TestCaseGenerateRequest,
    TestCaseGenerateResponse,
)
from app.services.testcase_service import TestCaseService

router = APIRouter()


@router.post("/generate", response_model=TestCaseGenerateResponse)
async def generate_test_cases(
    request: TestCaseGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate test cases from an analyzed document using AI.

    LEARN: Request body with Pydantic model
    - FastAPI reads JSON body
    - Validates it against TestCaseGenerateRequest schema
    - If validation fails → automatic 422 error with details
    """
    service = TestCaseService(db)
    return await service.generate(request)


@router.get("/", response_model=list[TestCaseResponse])
async def list_test_cases(
    project_id: int = Query(..., description="Filter by project ID"),
    case_type: str | None = Query(None, description="Filter: positive, negative, edge"),
    status_filter: str | None = Query(None, alias="status", description="Filter: draft, approved, rejected"),
    db: AsyncSession = Depends(get_db),
):
    """
    List test cases for a project with optional filters.

    LEARN: Query(...) vs Query(None)
    - Query(...) = REQUIRED query parameter
    - Query(None) = OPTIONAL query parameter (defaults to None)
    """
    service = TestCaseService(db)
    return await service.get_by_project(
        project_id=project_id,
        case_type=case_type,
        status=status_filter,
    )


@router.put("/{testcase_id}", response_model=TestCaseResponse)
async def update_test_case(
    testcase_id: int,
    update_data: TestCaseUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update or approve/reject a test case."""
    service = TestCaseService(db)
    testcase = await service.update(testcase_id, update_data)
    if not testcase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case with id {testcase_id} not found",
        )
    return testcase


@router.get("/export")
async def export_test_cases(
    project_id: int = Query(...),
    format: str = Query("csv", description="Export format: csv or excel"),
    db: AsyncSession = Depends(get_db),
):
    """
    Export test cases as CSV or Excel file.

    LEARN: StreamingResponse
    - Instead of returning JSON, we return a file download
    - Browser will download it automatically
    """
    service = TestCaseService(db)
    file_stream, filename = await service.export(project_id=project_id, format=format)
    return StreamingResponse(
        file_stream,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
