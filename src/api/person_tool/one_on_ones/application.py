from uuid import UUID

from person_tool.employees.models import EmployeeRole
from person_tool.factories.service_factory import service_factory
from person_tool.one_on_ones.models import (
    ActionItemRequest,
    ActionItemResponse,
    ActionItemStatusUpdate,
    OneOnOneNoteRequest,
    OneOnOneNoteResponse,
    OneOnOneSessionRequest,
    OneOnOneSessionResponse,
    OneOnOneTimelineEntry,
)


class OneOnOneApplication:
    def __init__(self) -> None:
        self.service_factory = service_factory

    async def create_session(
        self, *, request: OneOnOneSessionRequest
    ) -> OneOnOneSessionResponse:
        async with self.service_factory(use_transaction=True) as sf:
            return await sf.one_on_one_service.create_session(request=request)

    async def list_employee_sessions(
        self,
        *,
        employee_uid: UUID,
        viewer_role: EmployeeRole,
        viewer_uid: UUID,
        limit: int,
        offset: int,
    ) -> list[OneOnOneTimelineEntry]:
        async with self.service_factory(use_transaction=False) as sf:
            return await sf.one_on_one_service.list_employee_sessions(
                employee_uid=employee_uid,
                viewer_role=viewer_role,
                viewer_uid=viewer_uid,
                limit=limit,
                offset=offset,
            )

    async def add_note(
        self,
        *,
        session_uid: UUID,
        author_uid: UUID,
        request: OneOnOneNoteRequest,
    ) -> OneOnOneNoteResponse:
        async with self.service_factory(use_transaction=True) as sf:
            return await sf.one_on_one_service.add_note(
                session_uid=session_uid,
                author_uid=author_uid,
                request=request,
            )

    async def add_action_item(
        self,
        *,
        request: ActionItemRequest,
    ) -> ActionItemResponse:
        async with self.service_factory(use_transaction=True) as sf:
            return await sf.one_on_one_service.add_action_item(request=request)

    async def update_action_item_status(
        self, *, action_uid: UUID, request: ActionItemStatusUpdate
    ) -> ActionItemResponse:
        async with self.service_factory(use_transaction=True) as sf:
            return await sf.one_on_one_service.update_action_item_status(
                action_uid=action_uid,
                request=request,
            )

