"""
Script Repository (Phase 2)
=============================
Data access layer for Script model.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.script import Script


class ScriptRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, script: Script) -> Script:
        self.db.add(script)
        await self.db.flush()
        await self.db.refresh(script)
        return script

    async def get_by_id(self, script_id: int) -> Script | None:
        result = await self.db.execute(
            select(Script).where(Script.id == script_id)
        )
        return result.scalar_one_or_none()

    async def get_by_testcase(self, testcase_id: int) -> list[Script]:
        result = await self.db.execute(
            select(Script).where(Script.test_case_id == testcase_id)
        )
        return list(result.scalars().all())
