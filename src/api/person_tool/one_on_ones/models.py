from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class NoteVisibility(StrEnum):
    SHARED = "SHARED"
    PRIVATE = "PRIVATE"


class ActionStatus(StrEnum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class OneOnOneSessionRequest(BaseModel):
    manager_uid: UUID
    employee_uid: UUID
    session_date: date
    frequency: str | None = Field(default=None, max_length=32)
    agenda: str | None = None
    shared_summary: str | None = None

    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )


class OneOnOneSessionResponse(OneOnOneSessionRequest):
    uid: UUID
    created_at: datetime


class OneOnOneNoteRequest(BaseModel):
    visibility: NoteVisibility = NoteVisibility.SHARED
    content: str

    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )


class OneOnOneNoteResponse(BaseModel):
    uid: UUID
    session_uid: UUID
    author_uid: UUID
    visibility: NoteVisibility
    content: str
    created_at: datetime

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class ActionItemRequest(BaseModel):
    session_uid: UUID | None = Field(default=None)
    employee_uid: UUID
    description: str
    owner_uid: UUID
    due_date: date | None = None
    status: ActionStatus = ActionStatus.OPEN

    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )


class ActionItemResponse(ActionItemRequest):
    uid: UUID
    created_at: datetime
    updated_at: datetime


class ActionItemStatusUpdate(BaseModel):
    status: ActionStatus

    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )


class OneOnOneTimelineEntry(BaseModel):
    session: OneOnOneSessionResponse
    notes: list[OneOnOneNoteResponse]
    action_items: list[ActionItemResponse]

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

