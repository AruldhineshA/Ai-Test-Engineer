"""
Script Generation Endpoints (Phase 2)
=======================================
Converts approved test cases into automation scripts.
Supports Playwright (UI testing) and Artillery (load testing).

Endpoints:
- POST   /scripts/generate          → Generate (or regenerate) a script
- GET    /scripts/                  → List scripts for a test case
- GET    /scripts/{script_id}       → Get a single script's details
- GET    /scripts/{script_id}/download → Download script as a file
- DELETE /scripts/{script_id}       → Delete a script
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from io import BytesIO
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.script import ScriptGenerateRequest, ScriptResponse
from app.services.script_service import ScriptService

router = APIRouter()


# File extension lookup for downloads
_EXTENSIONS = {
    ("playwright", "python"): "py",
    ("playwright", "javascript"): "spec.js",
    ("artillery", "yaml"): "yml",
}


@router.post(
    "/generate",
    response_model=ScriptResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_script(
    request: ScriptGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate an automation script from a test case using AI.

    If a script of the same (test_case_id, script_type, language)
    already exists, its code is regenerated and updated in place.
    """
    service = ScriptService(db)
    return await service.generate(request)


@router.get("/", response_model=list[ScriptResponse])
async def list_scripts(
    test_case_id: int = Query(..., description="Filter scripts by test case ID"),
    db: AsyncSession = Depends(get_db),
):
    """List all generated scripts for a given test case."""
    service = ScriptService(db)
    return await service.list_by_testcase(test_case_id)


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(script_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single generated script by its ID."""
    service = ScriptService(db)
    script = await service.get_by_id(script_id)
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Script {script_id} not found",
        )
    return script


@router.get("/{script_id}/download")
async def download_script(script_id: int, db: AsyncSession = Depends(get_db)):
    """Download a script as a file with proper extension."""
    service = ScriptService(db)
    script = await service.get_by_id(script_id)
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Script {script_id} not found",
        )

    ext = _EXTENSIONS.get(
        (script.script_type, script.language),
        "txt",
    )
    filename = f"script_{script.test_case_id}_{script.script_type}.{ext}"

    file_stream = BytesIO(script.code_content.encode("utf-8"))
    return StreamingResponse(
        file_stream,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/{script_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_script(script_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a generated script."""
    service = ScriptService(db)
    deleted = await service.delete(script_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Script {script_id} not found",
        )
    return None
