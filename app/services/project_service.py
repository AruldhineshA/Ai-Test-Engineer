"""
Project Service
================
Business logic for project operations.

LEARN: Service Pattern
- Routes call Services (not repositories directly)
- Services contain the "business rules"
- Services call Repositories for data access

FLOW: Route → Service → Repository → Database
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.schemas.project import ProjectCreate


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: ProjectCreate) -> Project:
        """Create a new project."""
        project = Project(
            name=data.name,
            description=data.description,
        )
        self.db.add(project)
        await self.db.flush()
        await self.db.refresh(project)
        return project

    async def get_by_id(self, project_id: int) -> Project | None:
        """Get a single project by ID."""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[Project]:
        """Get all projects with pagination."""
        result = await self.db.execute(
            select(Project).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
