"""
Script Generation Prompts (Phase 2)
=====================================
Prompt templates for automation script generation.
"""

PLAYWRIGHT_SYSTEM_PROMPT = """You are an expert automation test engineer.
Generate clean, production-ready Playwright test scripts."""

PLAYWRIGHT_PROMPT = """Convert the following test case into a Playwright {language} script.

TEST CASE:
- Scenario: {scenario}
- Preconditions: {preconditions}
- Steps: {test_steps}
- Expected Result: {expected_result}

Generate a complete, runnable Playwright script:"""

ARTILLERY_PROMPT = """Convert the following test case into an Artillery load test YAML config.

TEST CASE:
- Scenario: {scenario}
- Steps: {test_steps}
- Expected Result: {expected_result}

Generate a complete Artillery config:"""
