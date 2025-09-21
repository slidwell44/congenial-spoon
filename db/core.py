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
        async def _init(init_con: Connection) -> None:
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
            init=_init,
        )
        async with self.connection() as con:
            await con.fetchval("SELECT 1")

    async def shutdown(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None

    @asynccontextmanager
    async def connection(self) -> t.AsyncIterator[Connection]:
        con = await self.pool.acquire()
        try:
            yield con
        finally:
            await self.pool.release(con)

    @asynccontextmanager
    async def transaction(self) -> t.AsyncIterator[Connection]:
        con = await self.pool.acquire()
        tr = con.transaction()
        await tr.start()
        try:
            yield con
            await tr.commit()
        except Exception:
            await tr.rollback()
            raise
        finally:
            await self.pool.release(con)


people_management_db = PeopleManagementDatabase()

__all__ = ["people_management_db"]
