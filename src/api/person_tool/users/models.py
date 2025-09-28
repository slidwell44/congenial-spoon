from __future__ import annotations

import typing as t
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field  # type: ignore
from pydantic.alias_generators import to_camel


class UserBase(BaseModel):
    id: str = Field(min_length=3, max_length=64, examples=["sl3789"])
    first_name: str = Field(min_length=1, max_length=100, examples=["Simon"])
    last_name: str = Field(min_length=1, max_length=100, examples=["Lidwell"])
    email: EmailStr = Field(examples=["slidwell@example.com"])

    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )


class CreateUserRequest(UserBase):
    pass


class UpdateUserRequest(BaseModel):
    uid: UUID
    id: str | None = Field(default=None, min_length=3, max_length=64)
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None

    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )


class UserResponse(UserBase):
    uid: UUID
    created_at: datetime
