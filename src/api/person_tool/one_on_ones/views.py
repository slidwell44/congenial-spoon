import typing as t
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Query, status

from person_tool.auth.dependencies import CurrentUser, get_current_user
from person_tool.dependencies import provide_one_on_one_application
from person_tool.one_on_ones.application import OneOnOneApplication
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

router = APIRouter()


@router.post(
    "/sessions",
    response_model=OneOnOneSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a 1:1 session",
)
async def create_session(
    application: t.Annotated[
        OneOnOneApplication, Depends(provide_one_on_one_application)
    ],
    request: OneOnOneSessionRequest = Body(...),
) -> OneOnOneSessionResponse:
    return await application.create_session(request=request)


@router.get(
    "/employees/{employee_uid}",
    response_model=list[OneOnOneTimelineEntry],
    status_code=status.HTTP_200_OK,
    summary="List 1:1 sessions for an employee",
)
async def list_employee_sessions(
    application: t.Annotated[
        OneOnOneApplication, Depends(provide_one_on_one_application)
    ],
    current_user: CurrentUser = Depends(get_current_user),
    employee_uid: UUID = Path(...),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[OneOnOneTimelineEntry]:
    return await application.list_employee_sessions(
        employee_uid=employee_uid,
        viewer_role=current_user.role,
        viewer_uid=current_user.uid,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/sessions/{session_uid}/notes",
    response_model=OneOnOneNoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a note to a session",
)
async def add_note(
    application: t.Annotated[
        OneOnOneApplication, Depends(provide_one_on_one_application)
    ],
    current_user: CurrentUser = Depends(get_current_user),
    session_uid: UUID = Path(...),
    request: OneOnOneNoteRequest = Body(...),
) -> OneOnOneNoteResponse:
    return await application.add_note(
        session_uid=session_uid,
        author_uid=current_user.uid,
        request=request,
    )


@router.post(
    "/sessions/{session_uid}/action-items",
    response_model=ActionItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an action item tied to a session",
)
async def create_action_item(
    application: t.Annotated[
        OneOnOneApplication, Depends(provide_one_on_one_application)
    ],
    session_uid: UUID = Path(...),
    request: ActionItemRequest = Body(...),
) -> ActionItemResponse:
    payload = request.model_copy(update={"session_uid": session_uid})
    return await application.add_action_item(request=payload)


@router.patch(
    "/action-items/{action_uid}",
    response_model=ActionItemResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Update the status of an action item",
)
async def update_action_item_status(
    application: t.Annotated[
        OneOnOneApplication, Depends(provide_one_on_one_application)
    ],
    action_uid: UUID = Path(...),
    request: ActionItemStatusUpdate = Body(...),
) -> ActionItemResponse:
    return await application.update_action_item_status(
        action_uid=action_uid,
        request=request,
    )

