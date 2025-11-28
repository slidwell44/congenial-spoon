from uuid import UUID

from fastapi import Header, HTTPException, status
from pydantic import BaseModel

from person_tool.employees.models import EmployeeRole


class CurrentUser(BaseModel):
    uid: UUID
    role: EmployeeRole


async def get_current_user(
    x_user_uid: str | None = Header(default=None, alias="X-User-Uid"),
    x_user_role: str | None = Header(default=None, alias="X-User-Role"),
) -> CurrentUser:
    if not x_user_uid or not x_user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Uid or X-User-Role header",
        )
    try:
        user_role = EmployeeRole[x_user_role.upper()]
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported user role: {x_user_role}",
        ) from exc

    try:
        user_uid = UUID(x_user_uid)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-User-Uid header",
        ) from exc

    return CurrentUser(uid=user_uid, role=user_role)

