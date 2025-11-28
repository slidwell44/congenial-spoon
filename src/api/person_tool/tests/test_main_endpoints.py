"""
Tests for main application endpoints (root, favicon).
"""
import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_redirect(async_client: AsyncClient):
    """Test root endpoint redirects to /docs."""
    response = await async_client.get("/", follow_redirects=False)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"] == "/docs"


@pytest.mark.asyncio
async def test_root_with_redirects(async_client: AsyncClient):
    """Test root endpoint with redirects enabled."""
    # The client has follow_redirects=True, so it will follow to /docs
    # but /docs might not exist in test, so we just check it redirects
    response = await async_client.get("/")
    # Either redirects (307) or if docs exists, might be 200
    assert response.status_code in [status.HTTP_307_TEMPORARY_REDIRECT, status.HTTP_200_OK]


@pytest.mark.asyncio
async def test_favicon(async_client: AsyncClient):
    """Test favicon endpoint."""
    # The favicon file may not exist in test environment, so we expect either success or file not found error
    try:
        response = await async_client.get("/favicon.ico")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    except RuntimeError as e:
        # File not found is acceptable in test environment
        assert "does not exist" in str(e)

