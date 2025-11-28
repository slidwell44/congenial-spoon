import typing as t
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Query, status
from fastapi.exceptions import HTTPException

from person_tool.auth.dependencies import CurrentUser, get_current_user
from person_tool.dependencies import provide_skill_application
from person_tool.skills.application import SkillApplication
from person_tool.skills.models import (
    CreateSkillRequest,
    EmployeeSkillAssignmentRequest,
    EmployeeSkillResponse,
    SkillMatrixResponse,
    SkillResponse,
    UpdateSkillRequest,
)

router = APIRouter()


@router.get(
    "/catalog",
    response_model=list[SkillResponse],
    status_code=status.HTTP_200_OK,
    summary="List or search skills in the catalog",
)
async def list_skill_catalog(
    application: t.Annotated[SkillApplication, Depends(provide_skill_application)],
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[SkillResponse]:
    return await application.list_catalog(
        search=search,
        category=category,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/catalog",
    response_model=list[SkillResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create skills in bulk",
)
async def create_skill_catalog_entries(
    application: t.Annotated[SkillApplication, Depends(provide_skill_application)],
    data: list[CreateSkillRequest] = Body(..., min_length=1),
) -> list[SkillResponse]:
    if len(data) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create more than 100 skills at once",
        )
    return await application.create_skills(data=data)


@router.patch(
    "/catalog/{uid}",
    response_model=SkillResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Update a skill definition",
)
async def update_skill(
    application: t.Annotated[SkillApplication, Depends(provide_skill_application)],
    uid: UUID = Path(...),
    data: UpdateSkillRequest = Body(...),
) -> SkillResponse:
    if data.uid != uid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UID mismatch between path and payload",
        )
    return await application.update_skill(data=data)


@router.get(
    "/assignments/{employee_uid}",
    response_model=list[EmployeeSkillResponse],
    status_code=status.HTTP_200_OK,
    summary="List skills for an employee",
)
async def list_employee_skills(
    application: t.Annotated[SkillApplication, Depends(provide_skill_application)],
    employee_uid: UUID = Path(..., alias="employeeUid"),
) -> list[EmployeeSkillResponse]:
    return await application.list_employee_skills(employee_uid=employee_uid)


@router.post(
    "/assignments/{employee_uid}",
    response_model=EmployeeSkillResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign or update a skill for an employee",
)
async def upsert_employee_skill(
    application: t.Annotated[SkillApplication, Depends(provide_skill_application)],
    current_user: CurrentUser = Depends(get_current_user),
    employee_uid: UUID = Path(..., alias="employeeUid"),
    request: EmployeeSkillAssignmentRequest = Body(...),
) -> EmployeeSkillResponse:
    return await application.upsert_employee_skill(
        employee_uid=employee_uid,
        request=request,
        actor_uid=current_user.uid,
    )


@router.get(
    "/matrix",
    response_model=SkillMatrixResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a skill matrix for a manager's org",
)
async def get_skill_matrix(
    application: t.Annotated[SkillApplication, Depends(provide_skill_application)],
    manager_uid: UUID = Query(..., alias="managerUid"),
    skill_uids: list[UUID] | None = Query(
        default=None,
        alias="skillUid",
        description="List of skill UIDs to include. Repeat param for multiple.",
    ),
    min_level: int | None = Query(default=None, ge=0, le=4),
    depth: int = Query(default=2, ge=1, le=6),
) -> SkillMatrixResponse:
    return await application.get_skill_matrix(
        manager_uid=manager_uid,
        skill_uids=skill_uids,
        min_level=min_level,
        depth=depth,
    )

