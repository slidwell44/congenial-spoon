import collections.abc as c
from contextlib import asynccontextmanager

from asyncpg import Connection
from asyncpg.exceptions import InternalServerError

from person_tool.db.core import people_management_db
from person_tool.jobs.repository import JobRepository
from person_tool.jobs.service import JobService
from person_tool.system.repository import SystemRepository
from person_tool.system.service import SystemService
from person_tool.users.repository import UserRepository
from person_tool.users.service import UserService


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

        self._user_service: UserService | None = None
        self._job_service: JobService | None = None
        self._system_service: SystemService | None = None

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
    def user_service(self) -> UserService:
        if not self._user_service:
            user_repository: UserRepository = UserRepository(conn=self.connection)
            self._user_service = UserService(repository=user_repository)
        return self._user_service

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


@asynccontextmanager
async def service_factory(
    *, use_transaction: bool = False
) -> c.AsyncGenerator[ServiceFactory, None]:
    async with ServiceFactory(use_transaction=use_transaction) as sf:
        yield sf


__all__ = ["service_factory"]
