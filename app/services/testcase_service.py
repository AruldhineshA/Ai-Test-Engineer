"""
Test Case Service
==================
Business logic for test case generation, retrieval, and export.
This is the CORE service of Phase 1.

FLOW:
1. User triggers generation for an analyzed document
2. Service gets parsed content from document
3. Calls AI TestCaseGenerator → gets structured test cases
4. Saves test cases to DB via repository
5. Returns response with generated test cases
"""

import csv
import io
import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.testcase_generator import testcase_generator
from app.db.repositories.document_repo import DocumentRepository
from app.db.repositories.testcase_repo import TestCaseRepository
from app.models.testcase import TestCase
from app.schemas.testcase import (
    TestCaseGenerateRequest,
    TestCaseGenerateResponse,
    TestCaseResponse,
    TestCaseUpdate,
)

logger = logging.getLogger(__name__)


class TestCaseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TestCaseRepository(db)
        self.doc_repo = DocumentRepository(db)

    async def generate(self, request: TestCaseGenerateRequest) -> TestCaseGenerateResponse:
        """
        Generate test cases from an analyzed document.

        STEPS:
        1. Get document and check it's analyzed
        2. Call AI TestCaseGenerator with document content
        3. Create TestCase model instances
        4. Bulk save to DB
        5. Return response
        """
        # 1. Get the document
        document = await self.doc_repo.get_by_id(request.document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {request.document_id} not found",
            )

        # Check document has been analyzed (has parsed content)
        if not document.parsed_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document must be analyzed first. Call POST /documents/{id}/analyze",
            )

        try:
            # 2. Call AI Test Case Generator
            ai_test_cases = await testcase_generator.generate(
                parsed_content=document.parsed_content,
                include_positive=request.include_positive,
                include_negative=request.include_negative,
                include_edge=request.include_edge,
            )

            if not ai_test_cases:
                return TestCaseGenerateResponse(
                    document_id=request.document_id,
                    total_generated=0,
                    test_cases=[],
                    message="AI could not generate test cases from this document. "
                            "Try a document with clearer requirements.",
                )

            # 3. Create TestCase model instances
            testcase_models = []
            for tc_data in ai_test_cases:
                tc = TestCase(
                    project_id=document.project_id,
                    document_id=document.id,
                    test_case_id=tc_data["test_case_id"],
                    scenario=tc_data["scenario"],
                    preconditions=tc_data["preconditions"],
                    test_steps=tc_data["test_steps"],
                    expected_result=tc_data["expected_result"],
                    case_type=tc_data["case_type"],
                    status="draft",
                )
                testcase_models.append(tc)

            # 4. Bulk save to DB
            saved_testcases = await self.repo.create_many(testcase_models)

            # 5. Return response
            return TestCaseGenerateResponse(
                document_id=request.document_id,
                total_generated=len(saved_testcases),
                test_cases=[
                    TestCaseResponse.model_validate(tc) for tc in saved_testcases
                ],
                message=f"Successfully generated {len(saved_testcases)} test cases "
                        f"from '{document.filename}'",
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Test case generation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Test case generation failed: {e}",
            )

    async def get_by_project(
        self,
        project_id: int,
        case_type: str | None = None,
        status: str | None = None,
    ) -> list[TestCase]:
        """Get test cases for a project with optional filters."""
        return await self.repo.get_by_project(
            project_id=project_id,
            case_type=case_type,
            status=status,
        )

    async def update(self, testcase_id: int, update_data: TestCaseUpdate) -> TestCase | None:
        """Update a test case (e.g., approve/reject)."""
        return await self.repo.update(
            testcase_id,
            update_data.model_dump(exclude_none=True),
        )

    async def export(self, project_id: int, format: str = "csv") -> tuple[io.BytesIO, str]:
        """
        Export test cases as CSV file.

        Creates a file in memory (BytesIO) → FastAPI streams it as a download.
        No temporary files needed on disk.
        """
        testcases = await self.repo.get_by_project(project_id)

        if not testcases:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No test cases found for project {project_id}",
            )

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow([
            "Test Case ID", "Scenario", "Preconditions",
            "Test Steps", "Expected Result", "Type", "Status",
        ])

        # Data rows
        for tc in testcases:
            steps_text = " | ".join(
                f"{s['step_number']}. {s['action']}"
                for s in tc.test_steps
            ) if isinstance(tc.test_steps, list) else str(tc.test_steps)

            writer.writerow([
                tc.test_case_id, tc.scenario, tc.preconditions,
                steps_text, tc.expected_result, tc.case_type, tc.status,
            ])

        # Convert to bytes for streaming
        byte_output = io.BytesIO(output.getvalue().encode("utf-8"))
        byte_output.seek(0)
        filename = f"testcases_project_{project_id}.csv"

        return byte_output, filename
