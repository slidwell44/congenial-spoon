from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from person_tool.employees.models import (
    EmployeeResponse,
    EmployeeRole,
    EmployeeStatus,
    MyOrgResponse,
)
from person_tool.employees.service import EmployeeService


class FakeEmployeeRepository:
    def __init__(self, tree, open_roles):
        self._tree = tree
        self._open_roles = open_roles

    async def get_org_subtree(self, *, root_uid, max_depth):
        return self._tree

    async def get_open_role_counts(self, *, manager_uids):
        return self._open_roles


def build_employee(uid: UUID, first: str, last: str, role: EmployeeRole, manager: UUID | None):
    now = datetime.now(timezone.utc)
    return EmployeeResponse(
        uid=uid,
        employee_id=first.lower(),
        first_name=first,
        last_name=last,
        email=f"{first}.{last}@example.com",
        title="Role",
        department="Engineering",
        location="Remote",
        manager_uid=manager,
        role=role,
        status=EmployeeStatus.ACTIVE,
        hire_date=None,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_get_org_tree_summarizes_counts():
    root_uid = uuid4()
    manager_uid = uuid4()
    ic_uid = uuid4()

    employees = {
        root_uid: build_employee(root_uid, "Rosa", "Root", EmployeeRole.SENIOR_MANAGER, None),
        manager_uid: build_employee(manager_uid, "Manny", "Manager", EmployeeRole.MANAGER, root_uid),
        ic_uid: build_employee(ic_uid, "Ivy", "Ic", EmployeeRole.IC, manager_uid),
    }

    repo = FakeEmployeeRepository(
        tree=[
            {"employee": employees[root_uid], "depth": 0},
            {"employee": employees[manager_uid], "depth": 1},
            {"employee": employees[ic_uid], "depth": 2},
        ],
        open_roles={root_uid: 1, manager_uid: 0},
    )
    service = EmployeeService(repository=repo)  # type: ignore[arg-type]

    response: MyOrgResponse = await service.get_org_tree(root_uid=root_uid, depth=3)

    assert response.root.employee.uid == root_uid
    assert response.root.summary.total_reports == 2
    assert response.root.summary.manager_count == 1
    assert response.root.summary.ic_count == 1
    assert response.root.summary.open_roles == 1
    assert len(response.root.direct_reports) == 1
    assert response.root.direct_reports[0].employee.uid == manager_uid

