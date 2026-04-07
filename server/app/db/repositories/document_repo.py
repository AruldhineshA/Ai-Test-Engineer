"""
Document Repository
====================
Data access layer for Document model.

LEARN: Repository Pattern
- Repositories handle ALL database operations (CRUD)
- Services call repositories — never talk to DB directly
- This separation makes code testable and clean

WHY THIS PATTERN?
- If you change from PostgreSQL to MongoDB later,
  you only change repository files — not services or routes
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, document: Document) -> Document:
        self.db.add(document)
        await self.db.flush()  # Gets the auto-generated ID without committing
        await self.db.refresh(document)
        return document

    async def get_by_id(self, document_id: int) -> Document | None:
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def get_by_project(self, project_id: int) -> list[Document]:
        result = await self.db.execute(
            select(Document).where(Document.project_id == project_id)
        )
        return list(result.scalars().all())

    async def update_status(self, document_id: int, status: str) -> Document | None:
        document = await self.get_by_id(document_id)
        if document:
            document.status = status
            await self.db.flush()
            await self.db.refresh(document)
        return document
