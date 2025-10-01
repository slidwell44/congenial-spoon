from asyncpg import Connection


class SystemRepository:
    def __init__(self, conn: Connection) -> None:
        self.conn: Connection = conn

    async def check_system_readiness(self) -> bool:
        result = await self.conn.execute("SELECT 1")
        return bool(result)
