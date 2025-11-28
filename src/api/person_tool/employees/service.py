from collections import defaultdict
from uuid import UUID

from fastapi import status
from fastapi.exceptions import HTTPException

from person_tool.employees.models import (
    CreateEmployeeRequest,
    EmployeeResponse,
    EmployeeRole,
    EmployeeStatus,
    MyOrgResponse,
    OrgNode,
    OrgSummary,
    UpdateEmployeeRequest,
)
from person_tool.employees.repository import EmployeeRepository


class EmployeeService:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository

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
        employees = await self.repository.list_employees(
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            department=department,
            manager_uid=manager_uid,
            role=role.value if role else None,
            status=status_filter.value if status_filter else None,
            limit=limit,
            offset=offset,
        )
        if not employees:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employees not found",
            )
        return employees

    async def get_employee_by_id(self, uid: UUID) -> EmployeeResponse:
        employee = await self.repository.get_employee_by_uid(uid=uid)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with uid: {uid} not found",
            )
        return employee

    async def create_employees(
        self, *, data: list[CreateEmployeeRequest]
    ) -> list[EmployeeResponse]:
        return await self.repository.create_employees(data=data)

    async def update_employee(self, *, data: UpdateEmployeeRequest) -> EmployeeResponse:
        employee = await self.repository.update_employee(data=data)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with uid: {data.uid} not found",
            )
        return employee

    async def delete_employee(self, uid: UUID) -> None:
        result = await self.repository.delete_employee(uid=uid)
        if result != "DELETE 1":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with uid: {uid} not found",
            )

    async def get_org_tree(self, *, root_uid: UUID, depth: int = 3) -> MyOrgResponse:
        subtree = await self.repository.get_org_subtree(
            root_uid=root_uid, max_depth=depth
        )
        if not subtree:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with uid: {root_uid} not found",
            )

        employees = {
            item["employee"].uid: item["employee"] for item in subtree if item
        }
        children_map: dict[UUID, list[UUID]] = defaultdict(list)
        for item in subtree:
            employee: EmployeeResponse = item["employee"]
            if (
                employee.manager_uid
                and employee.manager_uid in employees
                and employee.uid != employee.manager_uid
            ):
                children_map[employee.manager_uid].append(employee.uid)

        for manager_uid, child_ids in children_map.items():
            children_map[manager_uid] = sorted(
                child_ids,
                key=lambda emp_uid: (
                    employees[emp_uid].last_name.lower(),
                    employees[emp_uid].first_name.lower(),
                ),
            )

        open_role_counts = await self.repository.get_open_role_counts(
            manager_uids=list(children_map.keys())
        )

        manager_roles = {EmployeeRole.MANAGER, EmployeeRole.SENIOR_MANAGER}

        def build_node(employee_uid: UUID) -> OrgNode:
            employee = employees[employee_uid]
            direct_reports = [
                build_node(child_uid) for child_uid in children_map.get(employee_uid, [])
            ]
            total_reports = sum(
                1 + child.summary.total_reports for child in direct_reports
            )
            manager_count = sum(
                (1 if child.employee.role in manager_roles else 0)
                + child.summary.manager_count
                for child in direct_reports
            )
            ic_count = sum(
                (1 if child.employee.role == EmployeeRole.IC else 0)
                + child.summary.ic_count
                for child in direct_reports
            )
            summary = OrgSummary(
                total_reports=total_reports,
                manager_count=manager_count,
                ic_count=ic_count,
                open_roles=open_role_counts.get(employee_uid, 0),
            )
            return OrgNode(employee=employee, direct_reports=direct_reports, summary=summary)

        root_node = build_node(root_uid)
        return MyOrgResponse(root=root_node)
