import pytest
from httpx import AsyncClient
from typing import AsyncGenerator
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    async with TestClient(
        app=app,
        base_url="http://test",
        backend="asyncio",
    ) as client:
        yield client


@pytest.fixture
def override_get_database_connection():
    """Fixture to override database connection for tests"""

    async def mock_get_database_connection():
        return None

    app.dependency_overrides = {
        "dependencies.get_database_connection": mock_get_database_connection
    }
    yield
    app.dependency_overrides = {}
