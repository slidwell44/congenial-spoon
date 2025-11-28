from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.alias_generators import to_camel


class EmployeeRole(StrEnum):
    ADMIN = "ADMIN"
    HR = "HR"
    SENIOR_MANAGER = "SENIOR_MANAGER"
    MANAGER = "MANAGER"
    IC = "IC"


class EmployeeStatus(StrEnum):
    ACTIVE = "ACTIVE"
    ON_LEAVE = "ON_LEAVE"
    TERMINATED = "TERMINATED"


class EmployeeBase(BaseModel):
    employee_id: str = Field(min_length=3, max_length=64, examples=["sl3789"])
    first_name: str = Field(min_length=1, max_length=100, examples=["Simon"])
    last_name: str = Field(min_length=1, max_length=100, examples=["Lidwell"])
    email: EmailStr = Field(examples=["slidwell@example.com"])
    title: str = Field(min_length=1, max_length=120, examples=["Engineering Manager"])
    department: str = Field(min_length=1, max_length=120, examples=["Engineering"])
    location: str | None = Field(
        default=None, max_length=120, examples=["Seattle", "Remote - EU"]
    )
    manager_uid: UUID | None = Field(default=None)
    role: EmployeeRole = Field(default=EmployeeRole.MANAGER)
    status: EmployeeStatus = Field(default=EmployeeStatus.ACTIVE)
    hire_date: date | None = Field(default=None)

    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )


class CreateEmployeeRequest(EmployeeBase):
    pass


class UpdateEmployeeRequest(BaseModel):
    uid: UUID
    employee_id: str | None = Field(default=None, min_length=3, max_length=64)
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    title: str | None = Field(default=None, min_length=1, max_length=120)
    department: str | None = Field(default=None, min_length=1, max_length=120)
    location: str | None = Field(default=None, max_length=120)
    manager_uid: UUID | None = Field(default=None)
    role: EmployeeRole | None = Field(default=None)
    status: EmployeeStatus | None = Field(default=None)
    hire_date: date | None = Field(default=None)

    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )


class EmployeeResponse(EmployeeBase):
    uid: UUID
    created_at: datetime
    updated_at: datetime


class OrgSummary(BaseModel):
    total_reports: int
    manager_count: int
    ic_count: int
    open_roles: int | None = None


class OrgNode(BaseModel):
    employee: EmployeeResponse
    direct_reports: list["OrgNode"]
    summary: OrgSummary

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class MyOrgResponse(BaseModel):
    root: OrgNode
