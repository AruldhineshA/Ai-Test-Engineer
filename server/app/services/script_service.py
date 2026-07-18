"""
Script Service (Phase 2)
==========================
Business logic for generating, listing, retrieving and deleting
automation scripts (Playwright + Artillery) from approved test cases.

FLOW for generation:
1. Receive a ScriptGenerateRequest (test_case_id, script_type, language)
2. Fetch the test case from DB (must exist)
3. Pass the test case to the AI engine (script_generator)
4. Save the generated code to the scripts table (or update if exists)
5. Return the saved Script row
"""

import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.script_generator import script_generator
from app.db.repositories.script_repo import ScriptRepository
from app.db.repositories.testcase_repo import TestCaseRepository
from app.models.script import Script
from app.schemas.script import ScriptGenerateRequest

logger = logging.getLogger(__name__)


class ScriptService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ScriptRepository(db)
        self.testcase_repo = TestCaseRepository(db)

    async def generate(self, request: ScriptGenerateRequest) -> Script:
        """Generate a script for a test case via the LLM and persist it."""
        # 1. Fetch test case
        testcase = await self.testcase_repo.get_by_id(request.test_case_id)
        if not testcase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test case {request.test_case_id} not found",
            )

        # 2. Build dict for the AI engine
        testcase_dict = {
            "test_case_id": testcase.test_case_id,
            "scenario": testcase.scenario,
            "preconditions": testcase.preconditions,
            "test_steps": testcase.test_steps,
            "expected_result": testcase.expected_result,
            "case_type": testcase.case_type,
        }

        # 3. Generate code via LLM
        try:
            code = await script_generator.generate(
                test_case=testcase_dict,
                script_type=request.script_type.value,
                language=request.language.value,
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            logger.error(f"Script generation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Script generation failed: {e}",
            )

        # 4. Save (or update existing of same type+language)
        existing = await self.repo.find_existing(
            test_case_id=request.test_case_id,
            script_type=request.script_type.value,
            language=request.language.value,
        )
        if existing:
            updated = await self.repo.update_code(existing.id, code)
            return updated

        new_script = Script(
            test_case_id=request.test_case_id,
            script_type=request.script_type.value,
            language=request.language.value,
            code_content=code,
            status="generated",
        )
        return await self.repo.create(new_script)

    async def get_by_id(self, script_id: int) -> Script | None:
        return await self.repo.get_by_id(script_id)

    async def list_by_testcase(self, test_case_id: int) -> list[Script]:
        return await self.repo.get_by_testcase(test_case_id)

    async def delete(self, script_id: int) -> bool:
        return await self.repo.delete(script_id)
