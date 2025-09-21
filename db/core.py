import typing as t
from contextlib import asynccontextmanager

from asyncpg import Pool, create_pool, Connection  # type: ignore

from config import settings


class PeopleManagementDatabase:
    def __init__(self):
        self._pool: Pool | None = None

    @property
    def pool(self) -> Pool:
        if self._pool is None:
            raise RuntimeError("Database not started. Call startup() first.")
        return self._pool

    async def startup(self):
        # noinspection PyUnusedLocal
        async def _init(init_con: Connection):
            await init_con.execute("SET TIME ZONE 'UTC'")

        self._pool = await create_pool(
            user=settings.database.user,
            password=settings.database.password,
            database=settings.database.db,
            host=settings.database.host,
            port=settings.database.port,
            min_size=settings.database.min_pool_size,
            max_size=settings.database.max_pool_size,
            command_timeout=settings.database.command_timeout,
        )
        async with self.connection() as con:
            await con.fetchval("SELECT 1")

    async def shutdown(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None

    @asynccontextmanager
    async def connection(self) -> t.AsyncIterator[Connection]:
        """
        I am not a big fan of committing transactions in the context manager, but
        this is a placeholder until I put in some kind of uow manager
        """
        con = await self._pool.acquire()
        try:
            con.transaction().start()
            yield con
            con.transaction().commit()
        except Exception:
            con.transaction().rollback()
            raise
        finally:
            await self._pool.release(con)


people_management_db = PeopleManagementDatabase()

__all__ = ["people_management_db"]
