"""
Test Case Repository
=====================
Data access layer for TestCase model.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.testcase import TestCase


class TestCaseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, testcase: TestCase) -> TestCase:
        self.db.add(testcase)
        await self.db.flush()
        await self.db.refresh(testcase)
        return testcase

    async def create_many(self, testcases: list[TestCase]) -> list[TestCase]:
        """Bulk insert multiple test cases at once."""
        self.db.add_all(testcases)
        await self.db.flush()
        for tc in testcases:
            await self.db.refresh(tc)
        return testcases

    async def get_by_id(self, testcase_id: int) -> TestCase | None:
        result = await self.db.execute(
            select(TestCase).where(TestCase.id == testcase_id)
        )
        return result.scalar_one_or_none()

    async def get_by_project(
        self,
        project_id: int,
        case_type: str | None = None,
        status: str | None = None,
    ) -> list[TestCase]:
        query = select(TestCase).where(TestCase.project_id == project_id)
        if case_type:
            query = query.where(TestCase.case_type == case_type)
        if status:
            query = query.where(TestCase.status == status)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, testcase_id: int, update_data: dict) -> TestCase | None:
        testcase = await self.get_by_id(testcase_id)
        if testcase:
            for key, value in update_data.items():
                if value is not None:
                    setattr(testcase, key, value)
            await self.db.flush()
            await self.db.refresh(testcase)
        return testcase
