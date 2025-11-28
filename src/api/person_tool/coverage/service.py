from uuid import UUID

from fastapi import status
from fastapi.exceptions import HTTPException

from person_tool.coverage.models import (
    CoverageReport,
    CreateRoleSkillProfile,
    RoleSkillProfileResponse,
)
from person_tool.coverage.repository import CoverageRepository


class CoverageService:
    def __init__(self, repository: CoverageRepository) -> None:
        self.repository = repository

    async def create_profile(
        self, *, request: CreateRoleSkillProfile
    ) -> RoleSkillProfileResponse:
        return await self.repository.create_role_skill_profile(request=request)

    async def get_profile(self, *, profile_uid: UUID) -> RoleSkillProfileResponse:
        try:
            return await self.repository.get_profile(profile_uid=profile_uid)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile {profile_uid} not found",
            ) from exc

    async def generate_report(
        self, *, manager_uid: UUID, profile_uid: UUID, depth: int
    ) -> CoverageReport:
        try:
            return await self.repository.generate_coverage_report(
                manager_uid=manager_uid,
                profile_uid=profile_uid,
                depth=depth,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc

