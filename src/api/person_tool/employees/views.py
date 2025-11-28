import typing as t
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Query, status
from fastapi.exceptions import HTTPException

from person_tool.dependencies import provide_employee_application
from person_tool.employees.application import EmployeeApplication
from person_tool.employees.models import (
    CreateEmployeeRequest,
    EmployeeResponse,
    EmployeeRole,
    EmployeeStatus,
    MyOrgResponse,
    UpdateEmployeeRequest,
)

router = APIRouter()


@router.get(
    path="/",
    response_model=list[EmployeeResponse],
    status_code=status.HTTP_200_OK,
    summary="Search employees",
)
async def list_employees(
    application: t.Annotated[
        EmployeeApplication, Depends(provide_employee_application)
    ],
    employee_id: str | None = Query(default=None, alias="employeeId"),
    first_name: str | None = Query(default=None, alias="firstName"),
    last_name: str | None = Query(default=None, alias="lastName"),
    department: str | None = Query(default=None),
    manager_uid: UUID | None = Query(default=None, alias="managerUid"),
    role: EmployeeRole | None = Query(default=None),
    status_filter: EmployeeStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[EmployeeResponse]:
    return await application.list_employees(
        employee_id=employee_id,
        first_name=first_name,
        last_name=last_name,
        department=department,
        manager_uid=manager_uid,
        role=role,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )


@router.get(
    path="/{uid}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get employee by UID",
)
async def get_employee(
    application: t.Annotated[
        EmployeeApplication, Depends(provide_employee_application)
    ],
    uid: UUID = Path(..., description="Employee UID"),
) -> EmployeeResponse:
    return await application.get_employee_by_id(uid=uid)


@router.get(
    path="/{uid}/org",
    response_model=MyOrgResponse,
    status_code=status.HTTP_200_OK,
    summary="Get org tree for a manager",
)
async def get_org_tree(
    application: t.Annotated[
        EmployeeApplication, Depends(provide_employee_application)
    ],
    uid: UUID = Path(..., description="Manager UID"),
    depth: int = Query(default=3, ge=1, le=6),
) -> MyOrgResponse:
    return await application.get_org_tree(root_uid=uid, depth=depth)


@router.post(
    path="/",
    response_model=list[EmployeeResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create employees",
)
async def create_employees(
    application: t.Annotated[
        EmployeeApplication, Depends(provide_employee_application)
    ],
    data: list[CreateEmployeeRequest] = Body(..., min_length=1),
) -> list[EmployeeResponse]:
    if len(data) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create more than 50 employees at once",
        )
    return await application.create_employees(data=data)


@router.patch(
    path="/{uid}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Update employee",
)
async def update_employee(
    application: t.Annotated[
        EmployeeApplication, Depends(provide_employee_application)
    ],
    uid: UUID = Path(..., description="Employee UID"),
    data: UpdateEmployeeRequest = Body(...),
) -> EmployeeResponse:
    if data.uid != uid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UID in payload must match URL parameter",
        )
    return await application.update_employee(data=data)


@router.delete(
    path="/{uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete employee",
)
async def delete_employee(
    application: t.Annotated[
        EmployeeApplication, Depends(provide_employee_application)
    ],
    uid: UUID = Path(..., description="Employee UID"),
) -> None:
    await application.delete_employee(uid=uid)
