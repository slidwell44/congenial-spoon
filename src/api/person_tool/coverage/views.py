import typing as t
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Query, status

from person_tool.auth.dependencies import CurrentUser, get_current_user
from person_tool.coverage.application import CoverageApplication
from person_tool.coverage.models import (
    CoverageReport,
    CreateRoleSkillProfile,
    RoleSkillProfileResponse,
)
from person_tool.dependencies import provide_coverage_application

router = APIRouter()


@router.post(
    "/profiles",
    response_model=RoleSkillProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a role or project skill profile",
)
async def create_profile(
    application: t.Annotated[
        CoverageApplication, Depends(provide_coverage_application)
    ],
    current_user: CurrentUser = Depends(get_current_user),
    request: CreateRoleSkillProfile = Body(...),
) -> RoleSkillProfileResponse:
    payload = request.model_copy(update={"owner_uid": request.owner_uid or current_user.uid})
    return await application.create_profile(request=payload)


@router.get(
    "/profiles/{profile_uid}",
    response_model=RoleSkillProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a specific profile",
)
async def get_profile(
    application: t.Annotated[
        CoverageApplication, Depends(provide_coverage_application)
    ],
    profile_uid: UUID = Path(...),
) -> RoleSkillProfileResponse:
    return await application.get_profile(profile_uid=profile_uid)


@router.get(
    "/teams/{manager_uid}",
    response_model=CoverageReport,
    status_code=status.HTTP_200_OK,
    summary="Generate a coverage report for a manager's org",
)
async def generate_coverage_report(
    application: t.Annotated[
        CoverageApplication, Depends(provide_coverage_application)
    ],
    manager_uid: UUID = Path(...),
    profile_uid: UUID = Query(..., alias="profileUid"),
    depth: int = Query(default=3, ge=1, le=6),
) -> CoverageReport:
    return await application.generate_report(
        manager_uid=manager_uid,
        profile_uid=profile_uid,
        depth=depth,
    )

