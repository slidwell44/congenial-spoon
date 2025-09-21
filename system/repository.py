from asyncpg import Connection


class SystemRepository:
    def __init__(self):
        pass

    @staticmethod
    async def check_system_readiness(conn: Connection) -> bool:
        result = await conn.execute("SELECT 1")
        return bool(result)
