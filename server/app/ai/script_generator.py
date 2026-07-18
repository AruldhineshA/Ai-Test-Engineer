"""
Script Generator (Phase 2)
============================
Converts an approved test case into a runnable automation script
(Playwright Python/JS or Artillery YAML) using the LLM.

FLOW:
1. Receive a test case dict + script_type + language
2. Pick the right prompt from prompts/script_prompts.py
3. Call llm_client.generate() — text response (NOT JSON)
4. Strip any stray markdown fences if present
5. Return raw code as a string
"""

import logging

from app.ai.llm_client import llm_client
from app.ai.prompts.script_prompts import PROMPT_REGISTRY

logger = logging.getLogger(__name__)


class ScriptGenerator:
    """Generates automation scripts from test cases via LLM."""

    async def generate(
        self,
        test_case: dict,
        script_type: str,
        language: str,
    ) -> str:
        """
        Generate a script for a single test case.

        Args:
            test_case: dict with keys: test_case_id, scenario, preconditions,
                       test_steps (list of dicts), expected_result, case_type
            script_type: "playwright" or "artillery"
            language: "python", "javascript" (for playwright) or "yaml" (for artillery)

        Returns:
            Raw code as a string, ready to save to DB / return to client.
        """
        key = (script_type.lower(), language.lower())
        if key not in PROMPT_REGISTRY:
            raise ValueError(
                f"Unsupported script_type+language combo: {script_type} + {language}. "
                f"Supported: {list(PROMPT_REGISTRY.keys())}"
            )

        system_prompt, user_prompt_template = PROMPT_REGISTRY[key]

        # Format test steps as a numbered list for the prompt
        steps_text = self._format_steps(test_case.get("test_steps", []))

        prompt = user_prompt_template.format(
            test_case_id=test_case.get("test_case_id", "TC-XXX"),
            scenario=test_case.get("scenario", ""),
            preconditions=test_case.get("preconditions", "None"),
            test_steps=steps_text,
            expected_result=test_case.get("expected_result", ""),
            case_type=test_case.get("case_type", "positive"),
        )

        try:
            # Script generation expects RAW CODE, not JSON.
            # Pass json_mode=False so Gemini doesn't wrap output in JSON.
            raw_response = await llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                json_mode=False,
            )
        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            raise RuntimeError(f"Failed to generate script: {e}") from e

        return self._clean_code(raw_response)

    def _format_steps(self, steps: list) -> str:
        """Render test_steps (list of dicts) as a numbered text block."""
        if not steps:
            return "  (no steps provided)"

        lines = []
        for idx, step in enumerate(steps, start=1):
            if isinstance(step, dict):
                action = step.get("action", "")
                expected = step.get("expected", "")
                line = f"  {idx}. {action}"
                if expected:
                    line += f"   (expected: {expected})"
                lines.append(line)
            elif isinstance(step, str):
                lines.append(f"  {idx}. {step}")
        return "\n".join(lines)

    @staticmethod
    def _clean_code(response: str) -> str:
        """Strip leading/trailing markdown fences if the LLM ignored instructions."""
        text = response.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)
        return text.strip() + "\n"


# Single instance used across the app
script_generator = ScriptGenerator()
