from uuid import UUID

from person_tool.coverage.models import (
    CoverageReport,
    CreateRoleSkillProfile,
    RoleSkillProfileResponse,
)
from person_tool.factories.service_factory import service_factory


class CoverageApplication:
    def __init__(self) -> None:
        self.service_factory = service_factory

    async def create_profile(
        self, *, request: CreateRoleSkillProfile
    ) -> RoleSkillProfileResponse:
        async with self.service_factory(use_transaction=True) as sf:
            return await sf.coverage_service.create_profile(request=request)

    async def get_profile(self, profile_uid: UUID) -> RoleSkillProfileResponse:
        async with self.service_factory(use_transaction=False) as sf:
            return await sf.coverage_service.get_profile(profile_uid=profile_uid)

    async def generate_report(
        self, *, manager_uid: UUID, profile_uid: UUID, depth: int
    ) -> CoverageReport:
        async with self.service_factory(use_transaction=False) as sf:
            return await sf.coverage_service.generate_report(
                manager_uid=manager_uid, profile_uid=profile_uid, depth=depth
            )

