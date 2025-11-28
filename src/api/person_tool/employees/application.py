from uuid import UUID

from person_tool.employees.models import (
    CreateEmployeeRequest,
    EmployeeResponse,
    EmployeeRole,
    EmployeeStatus,
    MyOrgResponse,
    UpdateEmployeeRequest,
)
from person_tool.factories.service_factory import service_factory


class EmployeeApplication:
    def __init__(self) -> None:
        self.service_factory = service_factory

    async def list_employees(
        self,
        *,
        employee_id: str | None,
        first_name: str | None,
        last_name: str | None,
        department: str | None,
        manager_uid: UUID | None,
        role: EmployeeRole | None,
        status_filter: EmployeeStatus | None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[EmployeeResponse]:
        async with self.service_factory(use_transaction=False) as sf:
            return await sf.employee_service.list_employees(
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

    async def get_employee_by_id(self, uid: UUID) -> EmployeeResponse:
        async with self.service_factory(use_transaction=False) as sf:
            return await sf.employee_service.get_employee_by_id(uid=uid)

    async def create_employees(
        self,
        data: list[CreateEmployeeRequest],
    ) -> list[EmployeeResponse]:
        async with self.service_factory(use_transaction=True) as sf:
            return await sf.employee_service.create_employees(data=data)

    async def update_employee(self, data: UpdateEmployeeRequest) -> EmployeeResponse:
        async with self.service_factory(use_transaction=True) as sf:
            return await sf.employee_service.update_employee(data=data)

    async def delete_employee(self, uid: UUID) -> None:
        async with self.service_factory(use_transaction=True) as sf:
            await sf.employee_service.delete_employee(uid=uid)

    async def get_org_tree(self, *, root_uid: UUID, depth: int) -> MyOrgResponse:
        async with self.service_factory(use_transaction=False) as sf:
            return await sf.employee_service.get_org_tree(root_uid=root_uid, depth=depth)
