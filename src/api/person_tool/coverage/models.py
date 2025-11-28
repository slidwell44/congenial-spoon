from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ProfileType(StrEnum):
    ROLE = "ROLE"
    PROJECT = "PROJECT"


class RoleSkillRequirement(BaseModel):
    skill_uid: UUID
    required_level: int = Field(ge=0, le=4)
    required_headcount: int = Field(ge=1, le=100)

    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )


class RoleSkillProfileBase(BaseModel):
    profile_type: ProfileType
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    owner_uid: UUID | None = None
    context: dict | None = None
    requirements: list[RoleSkillRequirement]

    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )


class CreateRoleSkillProfile(RoleSkillProfileBase):
    pass


class RoleSkillProfileResponse(RoleSkillProfileBase):
    uid: UUID
    created_at: datetime
    updated_at: datetime


class CoveragePerson(BaseModel):
    employee_uid: UUID
    employee_name: str
    level: int

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class SkillCoverageStat(BaseModel):
    skill_uid: UUID
    skill_name: str
    required_headcount: int
    required_level: int
    actual_headcount: int
    qualified_people: list[CoveragePerson]
    single_point_of_failure: bool

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class CoverageReport(BaseModel):
    manager_uid: UUID
    profile_uid: UUID
    generated_at: datetime
    stats: list[SkillCoverageStat]

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

