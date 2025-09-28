from __future__ import annotations

import typing as t
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field  # type: ignore
from pydantic.alias_generators import to_camel


class JobBase(BaseModel):
    id: str = Field(min_length=3, max_length=64, examples=["eng-001"])
    title: str = Field(min_length=1, max_length=200, examples=["Software Engineer"])
    description: str = Field(min_length=1, examples=["Develop and maintain software applications."])
    status: str = Field(min_length=1, max_length=50, examples=["active"])

    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )


class CreateJobRequest(JobBase):
    pass


class UpdateJobRequest(BaseModel):
    uid: UUID
    id: str | None = Field(default=None, min_length=3, max_length=64)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1)
    status: str | None = Field(default=None, min_length=1, max_length=50)

    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )


class JobResponse(JobBase):
    uid: UUID
    created_at: datetime
