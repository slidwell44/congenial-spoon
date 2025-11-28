"""
Tests for system endpoints.
"""
import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_system_readiness(async_client: AsyncClient, api_base_url: str):
    """Test system readiness check."""
    response = await async_client.get(f"{api_base_url}/system/ready")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"

