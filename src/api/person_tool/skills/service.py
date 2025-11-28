from uuid import UUID

from fastapi import status
from fastapi.exceptions import HTTPException

from person_tool.skills.models import (
    CreateSkillRequest,
    EmployeeSkillAssignmentRequest,
    EmployeeSkillResponse,
    SkillMatrixResponse,
    SkillResponse,
    UpdateSkillRequest,
)
from person_tool.skills.repository import SkillRepository


class SkillService:
    def __init__(self, repository: SkillRepository) -> None:
        self.repository = repository

    async def list_catalog(
        self,
        *,
        search: str | None,
        category: str | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[SkillResponse]:
        skills = await self.repository.list_catalog(
            search=search,
            category=category,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )
        if not skills:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No skills found",
            )
        return skills

    async def create_skills(
        self, *, data: list[CreateSkillRequest]
    ) -> list[SkillResponse]:
        return await self.repository.create_skills(data=data)

    async def update_skill(self, *, data: UpdateSkillRequest) -> SkillResponse:
        skill = await self.repository.update_skill(data=data)
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skill with uid {data.uid} not found",
            )
        return skill

    async def list_employee_skills(self, *, employee_uid: UUID) -> list[EmployeeSkillResponse]:
        return await self.repository.list_employee_skills(employee_uid=employee_uid)

    async def upsert_employee_skill(
        self,
        *,
        employee_uid: UUID,
        request: EmployeeSkillAssignmentRequest,
        actor_uid: UUID,
    ) -> EmployeeSkillResponse:
        return await self.repository.upsert_employee_skill(
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
        return await self.repository.get_skill_matrix(
            manager_uid=manager_uid,
            skill_uids=skill_uids if skill_uids else None,
            min_level=min_level,
            depth=depth,
        )

