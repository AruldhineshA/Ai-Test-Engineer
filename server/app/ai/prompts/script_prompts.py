"""
Script Generation Prompts (Phase 2)
=====================================
Prompt templates for converting approved test cases into runnable
automation scripts (Playwright + Artillery).

Design notes:
- Prompts force the LLM to return ONLY code (no markdown, no commentary)
- Selectors are intentionally placeholders (e.g. "[data-testid=...]") because
  Phase 2 generates from text-only specs. Real selectors arrive in Phase 3
  (URL crawling) when we can inspect actual DOM.
- Each prompt instructs the LLM to add `# TODO` markers wherever a human
  needs to fill in real values (URLs, credentials, selectors).
"""

# ─────────────────────────────────────────────────────────────────
# PLAYWRIGHT — Python (pytest-playwright)
# ─────────────────────────────────────────────────────────────────

PLAYWRIGHT_PYTHON_SYSTEM_PROMPT = """You are a senior QA automation engineer.
You write production-grade Playwright tests in Python using the pytest-playwright framework.
Your code is clean, idiomatic, well-commented, and follows best practices."""

PLAYWRIGHT_PYTHON_PROMPT = """Convert the following test case into a runnable Playwright Python test.

TEST CASE:
- ID: {test_case_id}
- Scenario: {scenario}
- Preconditions: {preconditions}
- Steps:
{test_steps}
- Expected Result: {expected_result}
- Type: {case_type}

REQUIREMENTS:
1. Use pytest-playwright with the `page: Page` fixture (sync API)
2. Function name must follow pytest convention: test_<snake_case_scenario>
3. Use `expect(...)` from playwright.sync_api for ALL assertions
4. Use semantic locators when possible: page.get_by_role(), page.get_by_label(), page.get_by_text()
5. For unknown selectors, use placeholders like page.locator("[data-testid=TODO_xxx]") and add a # TODO comment
6. Add a docstring describing what the test verifies
7. Add # TODO comments wherever the engineer needs to fill in real values (URL, credentials, etc.)
8. For preconditions like "user is logged in", create a setup section at the top with # TODO comments
9. Handle waits properly using expect() (auto-waiting) — do NOT use time.sleep()
10. For negative tests, assert the error state (e.g. expect(error_message).to_be_visible())

OUTPUT FORMAT:
Return ONLY the Python code. No markdown fences, no explanations, no preamble.
Start directly with the imports.

Generate the test now:"""


# ─────────────────────────────────────────────────────────────────
# PLAYWRIGHT — JavaScript (@playwright/test)
# ─────────────────────────────────────────────────────────────────

PLAYWRIGHT_JS_SYSTEM_PROMPT = """You are a senior QA automation engineer.
You write production-grade Playwright tests in JavaScript using @playwright/test.
Your code is clean, idiomatic, follows the latest Playwright patterns, and uses ESM imports."""

PLAYWRIGHT_JS_PROMPT = """Convert the following test case into a runnable Playwright JavaScript test.

TEST CASE:
- ID: {test_case_id}
- Scenario: {scenario}
- Preconditions: {preconditions}
- Steps:
{test_steps}
- Expected Result: {expected_result}
- Type: {case_type}

REQUIREMENTS:
1. Use @playwright/test framework — import {{ test, expect }} from '@playwright/test'
2. Test name must be descriptive (matches the scenario)
3. Use `expect(locator).toXxx()` for ALL assertions (auto-waiting)
4. Use semantic locators: page.getByRole(), page.getByLabel(), page.getByText()
5. For unknown selectors, use page.locator('[data-testid="TODO_xxx"]') with // TODO comment
6. Add JSDoc comment above the test describing what it verifies
7. Add // TODO comments wherever the engineer needs to fill in real values
8. For preconditions like "user is logged in", use test.beforeEach() with TODO setup
9. Use proper async/await — no .then() chains
10. For negative tests, assert error visibility (await expect(errorMsg).toBeVisible())

OUTPUT FORMAT:
Return ONLY the JavaScript code. No markdown fences, no explanations, no preamble.
Start directly with the imports.

Generate the test now:"""


# ─────────────────────────────────────────────────────────────────
# ARTILLERY — Load testing YAML
# ─────────────────────────────────────────────────────────────────

ARTILLERY_SYSTEM_PROMPT = """You are a senior performance engineer.
You write Artillery load test configurations in YAML format.
Your configs follow Artillery best practices and are immediately runnable."""

ARTILLERY_PROMPT = """Convert the following test case into an Artillery load test YAML configuration.

TEST CASE:
- ID: {test_case_id}
- Scenario: {scenario}
- Preconditions: {preconditions}
- Steps:
{test_steps}
- Expected Result: {expected_result}
- Type: {case_type}

REQUIREMENTS:
1. Top-level keys: `config` and `scenarios`
2. config.target should be a TODO placeholder (e.g. "https://TODO_your_api.example.com")
3. config.phases must include a sensible warm-up + sustained load (e.g. 60s warm-up at 5 RPS, 120s sustained at 20 RPS)
4. Define scenarios as a list with `name` and `flow`
5. Each step should have proper HTTP method, URL, headers, and assertions (`expect`)
6. Use capture/json to extract values from responses for chained requests
7. Add comments (# ...) wherever the engineer needs to fill in details
8. For positive tests: assert status codes (200/201) and response time thresholds
9. For negative tests: assert error status codes (400/401/403/404)
10. For edge tests: simulate boundary load (e.g. spike phase)

OUTPUT FORMAT:
Return ONLY the YAML content. No markdown fences, no explanations.
Start directly with the `config:` line.

Generate the YAML now:"""


# ─────────────────────────────────────────────────────────────────
# Prompt selector — used by ScriptGenerator
# ─────────────────────────────────────────────────────────────────

PROMPT_REGISTRY = {
    ("playwright", "python"): (PLAYWRIGHT_PYTHON_SYSTEM_PROMPT, PLAYWRIGHT_PYTHON_PROMPT),
    ("playwright", "javascript"): (PLAYWRIGHT_JS_SYSTEM_PROMPT, PLAYWRIGHT_JS_PROMPT),
    ("artillery", "yaml"): (ARTILLERY_SYSTEM_PROMPT, ARTILLERY_PROMPT),
}
