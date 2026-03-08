"""
Script Generation Endpoints (Phase 2)
=======================================
Converts approved test cases into automation scripts.
Supports Playwright (UI testing) and Artillery (load testing).

NOTE: This is Phase 2 functionality. Skeleton is created now
so the project structure is complete from day one.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.script import ScriptGenerateRequest, ScriptResponse

router = APIRouter()


@router.post("/generate", response_model=ScriptResponse, status_code=status.HTTP_201_CREATED)
async def generate_script(
    request: ScriptGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate automation script from an approved test case.
    Supports: playwright (UI), artillery (load testing).

    Phase 2 — Implementation coming later.
    """
    # TODO: Implement in Phase 2
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Script generation will be available in Phase 2",
    )


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(script_id: int, db: AsyncSession = Depends(get_db)):
    """Get a generated script by ID."""
    # TODO: Implement in Phase 2
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Script generation will be available in Phase 2",
    )
