"""
Test Configuration
===================
Shared test fixtures used across all test files.

LEARN: pytest fixtures
- Functions decorated with @pytest.fixture
- Automatically run before each test that needs them
- Provide test data, DB sessions, API clients, etc.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    """
    Async test client for making API requests in tests.

    LEARN: AsyncClient replaces TestClient for async FastAPI apps.
    It can call your API endpoints without starting a real server.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
