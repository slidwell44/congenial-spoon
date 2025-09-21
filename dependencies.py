import typing as t

from asyncpg import Connection
from fastapi import Depends

from db.core import people_management_db
from system.repository import SystemRepository
from system.service import SystemService


async def get_database_connection() -> t.AsyncIterator[Connection]:
    async with people_management_db.connection() as conn:
        yield conn


def get_system_repository() -> SystemRepository:
    return SystemRepository()


def get_system_service(
    repository: SystemRepository = Depends(get_system_repository),
) -> SystemService:
    return SystemService(repository)
