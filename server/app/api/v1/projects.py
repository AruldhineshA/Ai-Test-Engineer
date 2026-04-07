"""
Project Endpoints
==================
Handles CRUD operations for projects.
All endpoints require authentication — user can only see their own projects.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.project_service import ProjectService

router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new testing project (owned by current user)."""
    service = ProjectService(db)
    return await service.create(project_in, user_id=current_user.id)


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List current user's projects with pagination."""
    service = ProjectService(db)
    return await service.get_by_user(user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single project by ID (must belong to current user)."""
    service = ProjectService(db)
    project = await service.get_by_id(project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    return project
