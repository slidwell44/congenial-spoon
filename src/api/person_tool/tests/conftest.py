from __future__ import annotations

import os
from datetime import datetime
from typing import AsyncGenerator
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Set test environment variables before importing app
os.environ.setdefault("APP_VERSION", "0.1.0")
os.environ.setdefault("APP_NAME", "person-tool-test")
os.environ.setdefault("APP_PORT", "8000")
os.environ.setdefault("APP_HOST", "localhost")
os.environ.setdefault("APP_RELOAD", "false")
os.environ.setdefault("APP_LOG_LEVEL", "INFO")
os.environ.setdefault("APP_BASE_API_URL", "/api/v1")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "test_db")
os.environ.setdefault("POSTGRES_USER", "test_user")
os.environ.setdefault("POSTGRES_PASSWORD", "test_password")
os.environ.setdefault("POSTGRES_MIN_POOL_SIZE", "1")
os.environ.setdefault("POSTGRES_MAX_POOL_SIZE", "5")

from person_tool.employees.models import (
    CreateEmployeeRequest,
    EmployeeResponse,
    EmployeeRole,
    EmployeeStatus,
    MyOrgResponse,
    OrgNode,
    OrgSummary,
    UpdateEmployeeRequest,
)
from person_tool.jobs.models import CreateJobRequest, JobResponse, UpdateJobRequest
from person_tool.main import app
from person_tool.config import settings
from person_tool.dependencies import (
    provide_employee_application,
    provide_job_application,
    provide_system_application,
)


class FakeEmployeeApplication:
    def __init__(self) -> None:
        self._now = datetime.utcnow()
        self._uid = uuid4()

    async def list_employees(
        self,
        *,
        employee_id: str | None,
        first_name: str | None,
        last_name: str | None,
        department: str | None,
        manager_uid: UUID | None,
        role: EmployeeRole | None,
        status_filter: EmployeeStatus | None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[EmployeeResponse]:
        employee = EmployeeResponse(
            uid=self._uid,
            employee_id=employee_id or "emp-001",
            first_name=first_name or "Jane",
            last_name=last_name or "Doe",
            email="jane.doe@example.com",
            title="Engineer",
            department=department or "Engineering",
            location="Remote",
            manager_uid=manager_uid,
            role=role or EmployeeRole.IC,
            status=status_filter or EmployeeStatus.ACTIVE,
            hire_date=None,
            created_at=self._now,
            updated_at=self._now,
        )
        return [employee]

    async def get_employee_by_id(self, uid: UUID) -> EmployeeResponse:
        return EmployeeResponse(
            uid=uid,
            employee_id="emp-123",
            first_name="John",
            last_name="Smith",
            email="john.smith@example.com",
            title="Manager",
            department="Engineering",
            location="Seattle",
            manager_uid=None,
            role=EmployeeRole.MANAGER,
            status=EmployeeStatus.ACTIVE,
            hire_date=None,
            created_at=self._now,
            updated_at=self._now,
        )

    async def create_employees(
        self,
        data: list[CreateEmployeeRequest],
    ) -> list[EmployeeResponse]:
        return [
            EmployeeResponse(
                uid=uuid4(),
                employee_id=item.employee_id,
                first_name=item.first_name,
                last_name=item.last_name,
                email=item.email,
                title=item.title,
                department=item.department,
                location=item.location,
                manager_uid=item.manager_uid,
                role=item.role,
                status=item.status,
                hire_date=item.hire_date,
                created_at=self._now,
                updated_at=self._now,
            )
            for item in data
        ]

    async def update_employee(self, data: UpdateEmployeeRequest) -> EmployeeResponse:
        return EmployeeResponse(
            uid=data.uid,
            employee_id=data.employee_id or "emp-001",
            first_name=data.first_name or "Updated",
            last_name=data.last_name or "Employee",
            email=data.email or "updated.employee@example.com",
            title=data.title or "Updated Title",
            department=data.department or "Updated Department",
            location=data.location or "Updated Location",
            manager_uid=data.manager_uid,
            role=data.role or EmployeeRole.IC,
            status=data.status or EmployeeStatus.ACTIVE,
            hire_date=data.hire_date,
            created_at=self._now,
            updated_at=self._now,
        )

    async def delete_employee(self, uid: UUID) -> None:  # pragma: no cover - trivial
        return None

    async def get_org_tree(self, *, root_uid: UUID, depth: int) -> MyOrgResponse:
        employee = await self.get_employee_by_id(uid=root_uid)
        summary = OrgSummary(
            total_reports=0,
            manager_count=0,
            ic_count=1,
            open_roles=None,
        )
        node = OrgNode(employee=employee, direct_reports=[], summary=summary)
        return MyOrgResponse(root=node)


class FakeJobApplication:
    def __init__(self) -> None:
        self._now = datetime.utcnow()
        self._uid = uuid4()

    async def get_jobs(
        self,
        *,
        job_id: str | None,
        title: str | None,
        job_status: str | None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[JobResponse]:
        job = JobResponse(
            uid=self._uid,
            id=job_id or "eng-001",
            title=title or "Engineer",
            description="Test job",
            status=job_status or "active",
            created_at=self._now,
        )
        return [job]

    async def get_job_by_id(self, uid: UUID) -> JobResponse:
        return JobResponse(
            uid=uid,
            id="eng-002",
            title="Senior Engineer",
            description="Senior role",
            status="active",
            created_at=self._now,
        )

    async def create_jobs(self, data: list[CreateJobRequest]) -> list[JobResponse]:
        return [
            JobResponse(
                uid=uuid4(),
                id=item.id,
                title=item.title,
                description=item.description,
                status=item.status,
                created_at=self._now,
            )
            for item in data
        ]

    async def update_job(self, data: UpdateJobRequest) -> JobResponse:
        return JobResponse(
            uid=data.uid,
            id=data.id or "eng-003",
            title=data.title or "Updated Job",
            description=data.description or "Updated description",
            status=data.status or "active",
            created_at=self._now,
        )

    async def delete_job(self, uid: UUID) -> None:  # pragma: no cover - trivial
        return None


class FakeSystemApplication:
    async def check_system_readiness(self) -> dict[str, str]:
        return {"status": "ok"}


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Shared async HTTP client against the FastAPI ASGI app.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        follow_redirects=True,
    ) as client:
        yield client


@pytest.fixture
def api_base_url() -> str:
    """
    Get the base API URL from settings.
    """
    return settings.app.base_api_url


@pytest.fixture(autouse=True)
def override_app_dependencies() -> AsyncGenerator[None, None]:
    """
    Override application layer dependencies with fakes for all tests.
    """
    app.dependency_overrides[provide_employee_application] = FakeEmployeeApplication
    app.dependency_overrides[provide_job_application] = FakeJobApplication
    app.dependency_overrides[provide_system_application] = FakeSystemApplication
    try:
        yield
    finally:
        app.dependency_overrides.clear()
