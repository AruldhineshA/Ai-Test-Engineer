"""
Project Service
================
Business logic for project operations.
Projects are now owned by users (user_id).
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.schemas.project import ProjectCreate


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: ProjectCreate, user_id: int) -> Project:
        """Create a new project owned by the user."""
        project = Project(
            name=data.name,
            description=data.description,
            user_id=user_id,
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

    async def get_by_user(self, user_id: int, skip: int = 0, limit: int = 20) -> list[Project]:
        """Get all projects owned by a specific user."""
        result = await self.db.execute(
            select(Project)
            .where(Project.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
