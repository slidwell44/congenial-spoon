import typing as t

from fastapi import APIRouter, Depends

from person_tool.dependencies import provide_system_application
from person_tool.system.application import SystemApplication

router = APIRouter()


@router.get("/ready")
async def check_system_readiness(
    application: t.Annotated[SystemApplication, Depends(provide_system_application)],
):
    """
    Check the readiness of the system
    """
    return await application.check_system_readiness()
