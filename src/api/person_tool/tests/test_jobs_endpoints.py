"""
Tests for job endpoints.
"""
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_jobs_success(async_client: AsyncClient, api_base_url: str):
    """Test successful job listing."""
    response = await async_client.get(f"{api_base_url}/jobs")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    job = data[0]
    assert "uid" in job
    assert "id" in job
    assert "title" in job
    assert "description" in job
    assert "status" in job
    assert "createdAt" in job


@pytest.mark.asyncio
async def test_get_jobs_with_filters(async_client: AsyncClient, api_base_url: str):
    """Test job listing with query parameters."""
    response = await async_client.get(
        f"{api_base_url}/jobs",
        params={
            "jobId": "eng-001",
            "title": "Engineer",
            "status": "active",
            "limit": 10,
            "offset": 0,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_jobs_pagination(async_client: AsyncClient, api_base_url: str):
    """Test job listing with pagination."""
    response = await async_client.get(
        f"{api_base_url}/jobs",
        params={"limit": 20, "offset": 5},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_job_by_id_success(async_client: AsyncClient, api_base_url: str):
    """Test successful job retrieval by UID."""
    job_uid = uuid4()
    response = await async_client.get(f"/api/v1/jobs/{job_uid}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["uid"] == str(job_uid)
    assert "id" in data
    assert "title" in data
    assert "description" in data
    assert "status" in data


@pytest.mark.asyncio
async def test_get_job_by_id_invalid_uuid(async_client: AsyncClient, api_base_url: str):
    """Test job retrieval with invalid UUID format."""
    response = await async_client.get("/api/v1/jobs/invalid-uuid")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_create_jobs_success(async_client: AsyncClient, api_base_url: str):
    """Test successful job creation."""
    jobs_data = [
        {
            "id": "eng-001",
            "title": "Software Engineer",
            "description": "Develop and maintain software applications.",
            "status": "active",
        }
    ]
    response = await async_client.post(
        f"{api_base_url}/jobs",
        json=jobs_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == "eng-001"
    assert data[0]["title"] == "Software Engineer"


@pytest.mark.asyncio
async def test_create_jobs_multiple(async_client: AsyncClient, api_base_url: str):
    """Test creating multiple jobs at once."""
    jobs_data = [
        {
            "id": f"eng-{i:03d}",
            "title": f"Engineer {i}",
            "description": f"Description for engineer {i}",
            "status": "active",
        }
        for i in range(1, 6)
    ]
    response = await async_client.post(
        f"{api_base_url}/jobs",
        json=jobs_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert len(data) == 5


@pytest.mark.asyncio
async def test_create_jobs_too_many(async_client: AsyncClient, api_base_url: str):
    """Test creating more than 50 jobs fails."""
    jobs_data = [
        {
            "id": f"eng-{i:03d}",
            "title": f"Engineer {i}",
            "description": f"Description {i}",
            "status": "active",
        }
        for i in range(51)
    ]
    response = await async_client.post(
        f"{api_base_url}/jobs",
        json=jobs_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot create more than 50 jobs" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_jobs_empty_list(async_client: AsyncClient, api_base_url: str):
    """Test creating jobs with empty list."""
    response = await async_client.post(
        f"{api_base_url}/jobs",
        json=[],
    )
    # Empty list is valid, should return empty list
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_create_jobs_invalid_data(async_client: AsyncClient, api_base_url: str):
    """Test creating jobs with invalid data."""
    jobs_data = [
        {
            "id": "ab",  # Too short (min 3 chars)
            "title": "Engineer",
            "description": "Test",
            "status": "active",
        }
    ]
    response = await async_client.post(
        f"{api_base_url}/jobs",
        json=jobs_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_create_jobs_missing_required_fields(async_client: AsyncClient, api_base_url: str):
    """Test creating jobs with missing required fields."""
    jobs_data = [
        {
            "id": "eng-001",
            # Missing title, description, status
        }
    ]
    response = await async_client.post(
        f"{api_base_url}/jobs",
        json=jobs_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_update_job_success(async_client: AsyncClient, api_base_url: str):
    """Test successful job update."""
    job_uid = uuid4()
    update_data = {
        "uid": str(job_uid),
        "title": "Senior Software Engineer",
        "description": "Updated description",
        "status": "active",
    }
    response = await async_client.patch(
        "/api/v1/jobs/",
        json=update_data,
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert data["uid"] == str(job_uid)


@pytest.mark.asyncio
async def test_update_job_partial(async_client: AsyncClient, api_base_url: str):
    """Test partial job update."""
    job_uid = uuid4()
    update_data = {
        "uid": str(job_uid),
        "title": "New Title",
    }
    response = await async_client.patch(
        "/api/v1/jobs/",
        json=update_data,
    )
    assert response.status_code == status.HTTP_202_ACCEPTED


@pytest.mark.asyncio
async def test_update_job_missing_uid(async_client: AsyncClient, api_base_url: str):
    """Test job update without UID."""
    update_data = {
        "title": "New Title",
    }
    response = await async_client.patch(
        "/api/v1/jobs/",
        json=update_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_delete_job_success(async_client: AsyncClient, api_base_url: str):
    """Test successful job deletion."""
    job_uid = uuid4()
    response = await async_client.delete(f"/api/v1/jobs/{job_uid}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""


@pytest.mark.asyncio
async def test_delete_job_invalid_uuid(async_client: AsyncClient, api_base_url: str):
    """Test job deletion with invalid UUID."""
    response = await async_client.delete("/api/v1/jobs/invalid-uuid")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_jobs_with_job_id_pattern(async_client: AsyncClient, api_base_url: str):
    """Test job listing with various job ID patterns."""
    for job_id in ["eng-001", "eng", "001"]:
        response = await async_client.get(
            f"{api_base_url}/jobs",
            params={"jobId": job_id},
        )
        assert response.status_code == status.HTTP_200_OK

