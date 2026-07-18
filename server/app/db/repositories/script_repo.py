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

    async def find_existing(
        self,
        test_case_id: int,
        script_type: str,
        language: str,
    ) -> Script | None:
        """Find an existing script of the same type+language for a test case."""
        result = await self.db.execute(
            select(Script).where(
                Script.test_case_id == test_case_id,
                Script.script_type == script_type,
                Script.language == language,
            )
        )
        return result.scalar_one_or_none()

    async def update_code(self, script_id: int, code_content: str) -> Script | None:
        script = await self.get_by_id(script_id)
        if script:
            script.code_content = code_content
            script.status = "generated"
            await self.db.flush()
            await self.db.refresh(script)
        return script

    async def delete(self, script_id: int) -> bool:
        script = await self.get_by_id(script_id)
        if script:
            await self.db.delete(script)
            await self.db.flush()
            return True
        return False
