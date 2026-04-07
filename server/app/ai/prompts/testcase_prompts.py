"""
Test Case Generation Prompts
==============================
All LLM prompt templates for test case generation.

LEARN: Prompt Engineering
- Keep prompts separate from code
- Use clear, structured instructions
- Define exact output format (JSON schema)
- Include examples for better accuracy
"""

SYSTEM_PROMPT = """You are an expert QA engineer. Your job is to generate
comprehensive, structured test cases from software requirement documents.

You must output test cases in valid JSON format."""

TESTCASE_GENERATION_PROMPT = """Analyze the following software requirement document
and generate structured test cases.

DOCUMENT CONTENT:
{document_content}

REQUIREMENTS:
- Generate {case_types} test cases
- Each test case must have: test_case_id, scenario, preconditions, test_steps, expected_result, case_type
- test_steps must be an array of objects with: step_number, action, expected
- case_type must be one of: positive, negative, edge
- Be thorough and cover all functional flows

OUTPUT FORMAT (JSON array):
[
  {{
    "test_case_id": "TC-001",
    "scenario": "Verify successful login with valid credentials",
    "preconditions": "User is registered and on the login page",
    "test_steps": [
      {{"step_number": 1, "action": "Enter valid email", "expected": "Email is accepted"}},
      {{"step_number": 2, "action": "Enter valid password", "expected": "Password is masked"}},
      {{"step_number": 3, "action": "Click Login button", "expected": "User is redirected to dashboard"}}
    ],
    "expected_result": "User successfully logs in and sees the dashboard",
    "case_type": "positive"
  }}
]

Generate test cases now:"""
