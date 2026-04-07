"""
Test Case Generator
====================
Uses AI to generate structured test cases from analyzed documents.
This is the CORE AI feature of Phase 1.

FLOW:
1. Receives parsed document content (text)
2. Builds a prompt using templates from prompts/testcase_prompts.py
3. Sends prompt to LLM via llm_client.generate()
4. Parses the JSON response
5. Returns structured test case dicts matching the TestCase model

OUTPUT FORMAT:
Each test case is a dict with:
- test_case_id: "TC-001" format
- scenario: Test description
- preconditions: Setup requirements
- test_steps: [{step_number, action, expected}, ...]
- expected_result: Final expected outcome
- case_type: "positive" | "negative" | "edge"
"""

import logging

from app.ai.llm_client import llm_client
from app.ai.prompts.testcase_prompts import (
    SYSTEM_PROMPT,
    TESTCASE_GENERATION_PROMPT,
)

logger = logging.getLogger(__name__)


class TestCaseGenerator:
    """Generates structured test cases using LLM."""

    async def generate(
        self,
        parsed_content: str,
        include_positive: bool = True,
        include_negative: bool = True,
        include_edge: bool = True,
    ) -> list[dict]:
        """
        Generate test cases from parsed document content.

        Args:
            parsed_content: Text extracted from the document
            include_positive: Generate positive/happy-path tests
            include_negative: Generate negative/error-path tests
            include_edge: Generate edge case tests

        Returns:
            List of test case dicts ready to be saved to DB
        """
        if not parsed_content.strip():
            logger.warning("Empty document content — cannot generate test cases")
            return []

        # Build the case_types string based on user selections
        case_types = self._build_case_types(
            include_positive, include_negative, include_edge
        )

        # Truncate content if too long for LLM context
        max_chars = 25000
        content = parsed_content
        if len(content) > max_chars:
            content = content[:max_chars] + "\n\n[Content truncated]"

        # Build the prompt from template
        prompt = TESTCASE_GENERATION_PROMPT.format(
            document_content=content,
            case_types=case_types,
        )

        try:
            # Call LLM
            response = await llm_client.generate(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
            )

            # Parse JSON response
            test_cases = llm_client.parse_json_response(response)

            # Validate and clean each test case
            validated = self._validate_test_cases(test_cases)

            logger.info(f"Generated {len(validated)} test cases")
            return validated

        except Exception as e:
            logger.error(f"Test case generation failed: {e}")
            raise RuntimeError(f"Failed to generate test cases: {e}") from e

    def _build_case_types(
        self,
        include_positive: bool,
        include_negative: bool,
        include_edge: bool,
    ) -> str:
        """Build a comma-separated string of requested case types."""
        types = []
        if include_positive:
            types.append("positive (happy path)")
        if include_negative:
            types.append("negative (error handling)")
        if include_edge:
            types.append("edge case (boundary conditions)")

        if not types:
            types = ["positive (happy path)"]

        return ", ".join(types)

    def _validate_test_cases(self, raw_cases: list) -> list[dict]:
        """
        Validate and normalize test cases from LLM response.

        Ensures each test case has all required fields.
        Assigns sequential IDs if missing.
        """
        if not isinstance(raw_cases, list):
            logger.error("LLM returned non-list response for test cases")
            return []

        validated = []
        for idx, tc in enumerate(raw_cases, start=1):
            if not isinstance(tc, dict):
                continue

            # Ensure required fields exist
            validated_tc = {
                "test_case_id": tc.get("test_case_id", f"TC-{idx:03d}"),
                "scenario": tc.get("scenario", ""),
                "preconditions": tc.get("preconditions", "None"),
                "test_steps": self._validate_steps(tc.get("test_steps", [])),
                "expected_result": tc.get("expected_result", ""),
                "case_type": self._validate_case_type(tc.get("case_type", "positive")),
            }

            # Skip if no scenario (invalid test case)
            if not validated_tc["scenario"]:
                continue

            validated.append(validated_tc)

        return validated

    def _validate_steps(self, steps: list) -> list[dict]:
        """Ensure test_steps is a list of valid step objects."""
        if not isinstance(steps, list):
            return [{"step_number": 1, "action": str(steps), "expected": ""}]

        validated = []
        for idx, step in enumerate(steps, start=1):
            if isinstance(step, dict):
                validated.append({
                    "step_number": step.get("step_number", idx),
                    "action": step.get("action", ""),
                    "expected": step.get("expected", ""),
                })
            elif isinstance(step, str):
                validated.append({
                    "step_number": idx,
                    "action": step,
                    "expected": "",
                })

        return validated

    def _validate_case_type(self, case_type: str) -> str:
        """Ensure case_type is one of the allowed values."""
        allowed = {"positive", "negative", "edge"}
        if case_type.lower() in allowed:
            return case_type.lower()
        return "positive"


# Single instance used across the app
testcase_generator = TestCaseGenerator()
