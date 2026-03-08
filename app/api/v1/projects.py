"""
Project Endpoints
==================
Handles CRUD operations for projects.
A project groups related documents and test cases together.

LEARN:
- APIRouter() creates a mini-app with its own routes
- Each function is a "path operation" (HTTP method + path)
- Type hints + Pydantic schemas = automatic validation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectList
from app.services.project_service import ProjectService

router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project_in: ProjectCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new testing project.

    LEARN: Depends(get_db) is "Dependency Injection"
    - FastAPI automatically creates a DB session
    - Passes it to this function
    - Closes it when done
    """
    service = ProjectService(db)
    return await service.create(project_in)


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    """
    List all projects with pagination.

    LEARN: skip & limit are "Query Parameters"
    - GET /projects?skip=0&limit=10
    - FastAPI parses them automatically from the URL
    """
    service = ProjectService(db)
    return await service.get_all(skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a single project by ID.

    LEARN: {project_id} is a "Path Parameter"
    - GET /projects/5 → project_id = 5
    - FastAPI auto-converts string "5" to int
    """
    service = ProjectService(db)
    project = await service.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    return project
