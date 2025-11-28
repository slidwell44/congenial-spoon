from uuid import UUID

from person_tool.factories.service_factory import service_factory
from person_tool.skills.models import (
    CreateSkillRequest,
    EmployeeSkillAssignmentRequest,
    EmployeeSkillResponse,
    SkillMatrixResponse,
    SkillResponse,
    UpdateSkillRequest,
)


class SkillApplication:
    def __init__(self) -> None:
        self.service_factory = service_factory

    async def list_catalog(
        self,
        *,
        search: str | None,
        category: str | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[SkillResponse]:
        async with self.service_factory(use_transaction=False) as sf:
            return await sf.skill_service.list_catalog(
                search=search,
                category=category,
                is_active=is_active,
                limit=limit,
                offset=offset,
            )

    async def create_skills(
        self, data: list[CreateSkillRequest]
    ) -> list[SkillResponse]:
        async with self.service_factory(use_transaction=True) as sf:
            return await sf.skill_service.create_skills(data=data)

    async def update_skill(self, data: UpdateSkillRequest) -> SkillResponse:
        async with self.service_factory(use_transaction=True) as sf:
            return await sf.skill_service.update_skill(data=data)

    async def list_employee_skills(
        self, *, employee_uid: UUID
    ) -> list[EmployeeSkillResponse]:
        async with self.service_factory(use_transaction=False) as sf:
            return await sf.skill_service.list_employee_skills(
                employee_uid=employee_uid
            )

    async def upsert_employee_skill(
        self,
        *,
        employee_uid: UUID,
        request: EmployeeSkillAssignmentRequest,
        actor_uid: UUID,
    ) -> EmployeeSkillResponse:
        async with self.service_factory(use_transaction=True) as sf:
            return await sf.skill_service.upsert_employee_skill(
                employee_uid=employee_uid,
                request=request,
                actor_uid=actor_uid,
            )

    async def get_skill_matrix(
        self,
        *,
        manager_uid: UUID,
        skill_uids: list[UUID] | None,
        min_level: int | None,
        depth: int,
    ) -> SkillMatrixResponse:
        async with self.service_factory(use_transaction=False) as sf:
            return await sf.skill_service.get_skill_matrix(
                manager_uid=manager_uid,
                skill_uids=skill_uids,
                min_level=min_level,
                depth=depth,
            )

