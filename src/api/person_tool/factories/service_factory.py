import collections.abc as c
from contextlib import asynccontextmanager

from asyncpg import Connection
from asyncpg.exceptions import InternalServerError

from person_tool.db.core import people_management_db
from person_tool.coverage.repository import CoverageRepository
from person_tool.coverage.service import CoverageService
from person_tool.employees.repository import EmployeeRepository
from person_tool.employees.service import EmployeeService
from person_tool.jobs.repository import JobRepository
from person_tool.jobs.service import JobService
from person_tool.one_on_ones.repository import OneOnOneRepository
from person_tool.one_on_ones.service import OneOnOneService
from person_tool.skills.repository import SkillRepository
from person_tool.skills.service import SkillService
from person_tool.system.repository import SystemRepository
from person_tool.system.service import SystemService


class ServiceFactoryError(InternalServerError):
    pass


class ServiceFactory:
    """
    Factory for per-request services.
    Ensures all services share the same connection/transaction.
    """

    def __init__(self, use_transaction: bool = False) -> None:
        self.use_transaction: bool = use_transaction
        self._conn: Connection | None = None

        self._employee_service: EmployeeService | None = None
        self._job_service: JobService | None = None
        self._system_service: SystemService | None = None
        self._skill_service: SkillService | None = None
        self._one_on_one_service: OneOnOneService | None = None
        self._coverage_service: CoverageService | None = None

    async def __aenter__(self):
        self._ctx = (
            people_management_db.transaction()
            if self.use_transaction
            else people_management_db.connection()
        )

        self._conn = await self._ctx.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._ctx.__aexit__(exc_type, exc, tb)
        self._conn = None

    @property
    def connection(self) -> Connection:
        if self._conn is None:
            raise ServiceFactoryError("ServiceFactory used outside of context manager")
        return self._conn

    @property
    def employee_service(self) -> EmployeeService:
        if not self._employee_service:
            employee_repository: EmployeeRepository = EmployeeRepository(
                conn=self.connection
            )
            self._employee_service = EmployeeService(repository=employee_repository)
        return self._employee_service

    @property
    def jobs_service(self) -> JobService:
        if not self._job_service:
            jobs_repository: JobRepository = JobRepository(self.connection)
            self._job_service = JobService(repository=jobs_repository)
        return self._job_service

    @property
    def system_service(self) -> SystemService:
        if not self._system_service:
            self._system_service = SystemService(SystemRepository(self.connection))
        return self._system_service

    @property
    def skill_service(self) -> SkillService:
        if not self._skill_service:
            repository = SkillRepository(self.connection)
            self._skill_service = SkillService(repository=repository)
        return self._skill_service

    @property
    def one_on_one_service(self) -> OneOnOneService:
        if not self._one_on_one_service:
            repository = OneOnOneRepository(self.connection)
            self._one_on_one_service = OneOnOneService(repository=repository)
        return self._one_on_one_service

    @property
    def coverage_service(self) -> CoverageService:
        if not self._coverage_service:
            repository = CoverageRepository(self.connection)
            self._coverage_service = CoverageService(repository=repository)
        return self._coverage_service


@asynccontextmanager
async def service_factory(
    *, use_transaction: bool = False
) -> c.AsyncGenerator[ServiceFactory, None]:
    async with ServiceFactory(use_transaction=use_transaction) as sf:
        yield sf


__all__ = ["service_factory"]
