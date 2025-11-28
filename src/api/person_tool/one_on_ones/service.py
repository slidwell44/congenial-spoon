from uuid import UUID

from fastapi import status
from fastapi.exceptions import HTTPException

from person_tool.employees.models import EmployeeRole
from person_tool.one_on_ones.models import (
    ActionItemRequest,
    ActionItemResponse,
    ActionItemStatusUpdate,
    NoteVisibility,
    OneOnOneNoteRequest,
    OneOnOneNoteResponse,
    OneOnOneSessionRequest,
    OneOnOneSessionResponse,
    OneOnOneTimelineEntry,
)
from person_tool.one_on_ones.repository import OneOnOneRepository


class OneOnOneService:
    def __init__(self, repository: OneOnOneRepository) -> None:
        self.repository = repository

    async def create_session(
        self, *, request: OneOnOneSessionRequest
    ) -> OneOnOneSessionResponse:
        return await self.repository.create_session(request=request)

    async def list_employee_sessions(
        self,
        *,
        employee_uid: UUID,
        viewer_role: EmployeeRole,
        viewer_uid: UUID,
        limit: int,
        offset: int,
    ) -> list[OneOnOneTimelineEntry]:
        timeline = await self.repository.list_employee_sessions(
            employee_uid=employee_uid,
            limit=limit,
            offset=offset,
        )
        filtered_entries: list[OneOnOneTimelineEntry] = []
        for entry in timeline:
            can_view_private = viewer_role in {
                EmployeeRole.ADMIN,
                EmployeeRole.HR,
            } or entry.session.manager_uid == viewer_uid
            notes = (
                entry.notes
                if can_view_private
                else [
                    note
                    for note in entry.notes
                    if note.visibility == NoteVisibility.SHARED
                ]
            )
            filtered_entries.append(
                OneOnOneTimelineEntry(
                    session=entry.session,
                    notes=notes,
                    action_items=entry.action_items,
                )
            )
        return filtered_entries

    async def add_note(
        self,
        *,
        session_uid: UUID,
        author_uid: UUID,
        request: OneOnOneNoteRequest,
    ) -> OneOnOneNoteResponse:
        return await self.repository.add_note(
            session_uid=session_uid, author_uid=author_uid, request=request
        )

    async def add_action_item(
        self,
        *,
        request: ActionItemRequest,
    ) -> ActionItemResponse:
        return await self.repository.add_action_item(request=request)

    async def update_action_item_status(
        self, *, action_uid: UUID, request: ActionItemStatusUpdate
    ) -> ActionItemResponse:
        action = await self.repository.update_action_item_status(
            action_uid=action_uid, request=request
        )
        if not action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Action item {action_uid} not found",
            )
        return action

