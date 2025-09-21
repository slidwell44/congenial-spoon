import typing as t
from os.path import defpath

from asyncpg import Connection
from fastapi import Depends

from db.core import people_management_db
from system.repository import SystemRepository
from system.service import SystemService
from users.repository import UserRepository
from users.service import UserService


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
