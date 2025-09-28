from asyncpg import Connection

from person_tool.system.repository import SystemRepository


class SystemService:
    def __init__(self, repository: SystemRepository):
        self.repository = repository

    async def check_system_readiness(self, conn: Connection) -> bool:
        return await self.repository.check_system_readiness(conn)
