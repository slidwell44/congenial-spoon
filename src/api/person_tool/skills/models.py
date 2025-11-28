from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class SkillSource(StrEnum):
    MANAGER = "MANAGER"
    IC_PROPOSAL = "IC_PROPOSAL"
    SYSTEM = "SYSTEM"


class SkillBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str | None = Field(default=None, max_length=64)
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    is_active: bool = True

    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )


class CreateSkillRequest(SkillBase):
    pass


class UpdateSkillRequest(BaseModel):
    uid: UUID
    name: str | None = Field(default=None, min_length=1, max_length=120)
    category: str | None = Field(default=None, max_length=64)
    description: str | None = Field(default=None)
    tags: list[str] | None = None
    is_active: bool | None = None

    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )


class SkillResponse(SkillBase):
    uid: UUID
    created_at: datetime
    updated_at: datetime


class EmployeeSkillAssignmentRequest(BaseModel):
    skill_uid: UUID = Field(alias="skillUid")
    level: int = Field(ge=0, le=4)
    notes: str | None = None
    source: SkillSource = SkillSource.MANAGER

    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )


class EmployeeSkillResponse(BaseModel):
    uid: UUID
    employee_uid: UUID
    skill_uid: UUID
    skill_name: str
    level: int
    source: SkillSource
    notes: str | None
    last_updated_by: UUID
    last_updated_at: datetime

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class SkillMatrixRow(BaseModel):
    employee_uid: UUID
    employee_name: str
    title: str
    skills: list[EmployeeSkillResponse]

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class SkillMatrixResponse(BaseModel):
    rows: list[SkillMatrixRow]

