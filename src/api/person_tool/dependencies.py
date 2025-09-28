import typing as t

from asyncpg import Connection
from fastapi import Depends

from person_tool.db.core import people_management_db
from person_tool.jobs.repository import JobRepository
from person_tool.jobs.service import JobService
from person_tool.system.repository import SystemRepository
from person_tool.system.service import SystemService
from person_tool.users.repository import UserRepository
from person_tool.users.service import UserService


# ---------------------- database dependencies ----------------------


async def get_database_connection() -> t.AsyncIterator[Connection]:
    async with people_management_db.connection() as conn:
        yield conn


async def get_database_transaction() -> t.AsyncIterator[Connection]:
    async with people_management_db.transaction() as conn:
        yield conn


# ---------------------- system dependencies ----------------------


def get_system_repository() -> SystemRepository:
    return SystemRepository()


def get_system_service(
    repository: SystemRepository = Depends(get_system_repository),
) -> SystemService:
    return SystemService(repository)


# ---------------------- user dependencies ----------------------


def get_user_repository() -> UserRepository:
    return UserRepository()


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repository)


# ---------------------- job dependencies ----------------------


def get_job_repository() -> JobRepository:
    return JobRepository()


def get_job_service(
    repository: JobRepository = Depends(get_job_repository),
) -> JobService:
    return JobService(repository)
