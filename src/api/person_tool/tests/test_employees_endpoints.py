"""
Tests for employee endpoints.
"""
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from person_tool.employees.models import (
    EmployeeRole,
    EmployeeStatus,
)


@pytest.mark.asyncio
async def test_list_employees_success(async_client: AsyncClient, api_base_url: str):
    """Test successful employee listing."""
    response = await async_client.get(f"{api_base_url}/employees")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    employee = data[0]
    assert "uid" in employee
    assert "employeeId" in employee
    assert "firstName" in employee
    assert "lastName" in employee
    assert "email" in employee


@pytest.mark.asyncio
async def test_list_employees_with_filters(async_client: AsyncClient, api_base_url: str):
    """Test employee listing with query parameters."""
    response = await async_client.get(
        f"{api_base_url}/employees",
        params={
            "employeeId": "emp-001",
            "firstName": "Jane",
            "lastName": "Doe",
            "department": "Engineering",
            "role": EmployeeRole.IC.value,
            "status": EmployeeStatus.ACTIVE.value,
            "limit": 10,
            "offset": 0,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_employees_with_manager_uid(async_client: AsyncClient, api_base_url: str):
    """Test employee listing filtered by manager UID."""
    manager_uid = uuid4()
    response = await async_client.get(
        f"{api_base_url}/employees",
        params={"managerUid": str(manager_uid)},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_employee_by_id_success(async_client: AsyncClient, api_base_url: str):
    """Test successful employee retrieval by UID."""
    employee_uid = uuid4()
    response = await async_client.get(f"{api_base_url}/employees/{employee_uid}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["uid"] == str(employee_uid)
    assert "employeeId" in data
    assert "firstName" in data
    assert "lastName" in data
    assert "email" in data


@pytest.mark.asyncio
async def test_get_employee_by_id_invalid_uuid(async_client: AsyncClient, api_base_url: str):
    """Test employee retrieval with invalid UUID format."""
    response = await async_client.get(f"{api_base_url}/employees/invalid-uuid")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_org_tree_success(async_client: AsyncClient, api_base_url: str):
    """Test successful org tree retrieval."""
    manager_uid = uuid4()
    response = await async_client.get(
        f"{api_base_url}/employees/{manager_uid}/org",
        params={"depth": 3},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "root" in data
    root = data["root"]
    assert "employee" in root
    assert "directReports" in root
    assert "summary" in root
    # Check for either camelCase or snake_case (Pydantic alias handling)
    assert "totalReports" in root["summary"] or "total_reports" in root["summary"]


@pytest.mark.asyncio
async def test_get_org_tree_with_depth(async_client: AsyncClient, api_base_url: str):
    """Test org tree retrieval with different depth values."""
    manager_uid = uuid4()
    for depth in [1, 3, 6]:
        response = await async_client.get(
            f"{api_base_url}/employees/{manager_uid}/org",
            params={"depth": depth},
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_org_tree_invalid_depth(async_client: AsyncClient, api_base_url: str):
    """Test org tree retrieval with invalid depth."""
    manager_uid = uuid4()
    # Depth too low
    response = await async_client.get(
        f"{api_base_url}/employees/{manager_uid}/org",
        params={"depth": 0},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Depth too high
    response = await async_client.get(
        f"{api_base_url}/employees/{manager_uid}/org",
        params={"depth": 7},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_create_employees_success(async_client: AsyncClient, api_base_url: str):
    """Test successful employee creation."""
    employees_data = [
        {
            "employeeId": "emp-001",
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "title": "Software Engineer",
            "department": "Engineering",
            "location": "Seattle",
            "role": EmployeeRole.IC.value,
            "status": EmployeeStatus.ACTIVE.value,
        }
    ]
    response = await async_client.post(
        f"{api_base_url}/employees",
        json=employees_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["employeeId"] == "emp-001"
    assert data[0]["firstName"] == "John"


@pytest.mark.asyncio
async def test_create_employees_multiple(async_client: AsyncClient, api_base_url: str):
    """Test creating multiple employees at once."""
    employees_data = [
        {
            "employeeId": f"emp-{i:03d}",
            "firstName": f"Employee{i}",
            "lastName": "Test",
            "email": f"employee{i}@example.com",
            "title": "Engineer",
            "department": "Engineering",
            "role": EmployeeRole.IC.value,
            "status": EmployeeStatus.ACTIVE.value,
        }
        for i in range(1, 6)
    ]
    response = await async_client.post(
        f"{api_base_url}/employees",
        json=employees_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert len(data) == 5


@pytest.mark.asyncio
async def test_create_employees_too_many(async_client: AsyncClient, api_base_url: str):
    """Test creating more than 50 employees fails."""
    employees_data = [
        {
            "employeeId": f"emp-{i:03d}",
            "firstName": f"Employee{i}",
            "lastName": "Test",
            "email": f"employee{i}@example.com",
            "title": "Engineer",
            "department": "Engineering",
            "role": EmployeeRole.IC.value,
            "status": EmployeeStatus.ACTIVE.value,
        }
        for i in range(51)
    ]
    response = await async_client.post(
        f"{api_base_url}/employees",
        json=employees_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot create more than 50 employees" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_employees_empty_list(async_client: AsyncClient, api_base_url: str):
    """Test creating employees with empty list fails validation."""
    response = await async_client.post(
        f"{api_base_url}/employees",
        json=[],
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_create_employees_invalid_data(async_client: AsyncClient, api_base_url: str):
    """Test creating employees with invalid data."""
    employees_data = [
        {
            "employeeId": "ab",  # Too short
            "firstName": "John",
            "lastName": "Doe",
            "email": "invalid-email",  # Invalid email
            "title": "Engineer",
            "department": "Engineering",
        }
    ]
    response = await async_client.post(
        f"{api_base_url}/employees",
        json=employees_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_update_employee_success(async_client: AsyncClient, api_base_url: str):
    """Test successful employee update."""
    employee_uid = uuid4()
    update_data = {
        "uid": str(employee_uid),
        "firstName": "Updated",
        "lastName": "Name",
        "title": "Senior Engineer",
    }
    response = await async_client.patch(
        f"{api_base_url}/employees/{employee_uid}",
        json=update_data,
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert data["uid"] == str(employee_uid)


@pytest.mark.asyncio
async def test_update_employee_uid_mismatch(async_client: AsyncClient, api_base_url: str):
    """Test employee update with UID mismatch between URL and body."""
    employee_uid = uuid4()
    other_uid = uuid4()
    update_data = {
        "uid": str(other_uid),
        "firstName": "Updated",
    }
    response = await async_client.patch(
        f"{api_base_url}/employees/{employee_uid}",
        json=update_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "UID in payload must match URL parameter" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_employee_partial(async_client: AsyncClient, api_base_url: str):
    """Test partial employee update."""
    employee_uid = uuid4()
    update_data = {
        "uid": str(employee_uid),
        "title": "New Title",
    }
    response = await async_client.patch(
        f"{api_base_url}/employees/{employee_uid}",
        json=update_data,
    )
    assert response.status_code == status.HTTP_202_ACCEPTED


@pytest.mark.asyncio
async def test_delete_employee_success(async_client: AsyncClient, api_base_url: str):
    """Test successful employee deletion."""
    employee_uid = uuid4()
    response = await async_client.delete(f"{api_base_url}/employees/{employee_uid}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""


@pytest.mark.asyncio
async def test_delete_employee_invalid_uuid(async_client: AsyncClient, api_base_url: str):
    """Test employee deletion with invalid UUID."""
    response = await async_client.delete(f"{api_base_url}/employees/invalid-uuid")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_list_employees_pagination(async_client: AsyncClient, api_base_url: str):
    """Test employee listing with pagination parameters."""
    response = await async_client.get(
        f"{api_base_url}/employees",
        params={"limit": 25, "offset": 0},
    )
    assert response.status_code == status.HTTP_200_OK

    response = await async_client.get(
        f"{api_base_url}/employees",
        params={"limit": 100, "offset": 10},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_list_employees_invalid_pagination(async_client: AsyncClient, api_base_url: str):
    """Test employee listing with invalid pagination."""
    # Limit too high
    response = await async_client.get(
        f"{api_base_url}/employees",
        params={"limit": 101},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Limit too low
    response = await async_client.get(
        f"{api_base_url}/employees",
        params={"limit": 0},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Negative offset
    response = await async_client.get(
        f"{api_base_url}/employees",
        params={"offset": -1},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

