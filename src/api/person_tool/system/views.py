import typing as t

from asyncpg import Connection
from fastapi import APIRouter, Depends

from person_tool.dependencies import get_system_service, get_database_connection
from person_tool.system.service import SystemService

router = APIRouter()


@router.get("/ready")
async def check_system_readiness(
    service: t.Annotated[SystemService, Depends(get_system_service)],
    conn: t.Annotated[Connection, Depends(get_database_connection)],
):
    """
    Check the readiness of the system
    """
    return await service.check_system_readiness(conn=conn)
