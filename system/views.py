import typing as t

from asyncpg import Connection
from fastapi import APIRouter, Depends

from dependencies import get_system_service, get_database_connection
from system.service import SystemService

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
