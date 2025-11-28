from collections import defaultdict
from uuid import UUID

from asyncpg import Connection
from asyncpg.protocol.protocol import Record

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
from person_tool.utils.audit import log_audit_event


class OneOnOneRepository:
    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    async def create_session(
        self, *, request: OneOnOneSessionRequest
    ) -> OneOnOneSessionResponse:
        row = await self.conn.fetchrow(
            """
            INSERT INTO people.one_on_one_sessions (
                manager_uid,
                employee_uid,
                session_date,
                frequency,
                agenda,
                shared_summary
            )
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING uid,
                      manager_uid,
                      employee_uid,
                      session_date,
                      frequency,
                      agenda,
                      shared_summary,
                      created_at;
            """,
            request.manager_uid,
            request.employee_uid,
            request.session_date,
            request.frequency,
            request.agenda,
            request.shared_summary,
        )
        session = OneOnOneSessionResponse.model_validate(dict(row))
        await log_audit_event(
            self.conn,
            entity_type="OneOnOneSession",
            entity_uid=session.uid,
            action="CREATE",
            performed_by=request.manager_uid,
            after=dict(row),
        )
        return session

    async def list_employee_sessions(
        self, *, employee_uid: UUID, limit: int, offset: int
    ) -> list[OneOnOneTimelineEntry]:
        sessions: list[Record] = await self.conn.fetch(
            """
            SELECT uid,
                   manager_uid,
                   employee_uid,
                   session_date,
                   frequency,
                   agenda,
                   shared_summary,
                   created_at
            FROM people.one_on_one_sessions
            WHERE employee_uid = $1
            ORDER BY session_date DESC
            LIMIT $2 OFFSET $3
            """,
            employee_uid,
            limit,
            offset,
        )
        if not sessions:
            return []

        session_ids = [row["uid"] for row in sessions]

        notes: list[Record] = await self.conn.fetch(
            """
            SELECT uid,
                   session_uid,
                   author_uid,
                   visibility,
                   content,
                   created_at
            FROM people.one_on_one_notes
            WHERE session_uid = ANY($1::uuid[])
            ORDER BY created_at ASC
            """,
            session_ids,
        )

        actions: list[Record] = await self.conn.fetch(
            """
            SELECT uid,
                   session_uid,
                   employee_uid,
                   description,
                   owner_uid,
                   due_date,
                   status,
                   created_at,
                   updated_at
            FROM people.action_items
            WHERE session_uid = ANY($1::uuid[])
            ORDER BY created_at DESC
            """,
            session_ids,
        )

        note_map: dict[UUID, list[OneOnOneNoteResponse]] = defaultdict(list)
        for note in notes:
            note_map[note["session_uid"]].append(
                OneOnOneNoteResponse.model_validate(dict(note))
            )

        action_map: dict[UUID, list[ActionItemResponse]] = defaultdict(list)
        for action in actions:
            action_map[action["session_uid"]].append(
                ActionItemResponse.model_validate(dict(action))
            )

        timeline: list[OneOnOneTimelineEntry] = []
        for session in sessions:
            session_model = OneOnOneSessionResponse.model_validate(dict(session))
            timeline.append(
                OneOnOneTimelineEntry(
                    session=session_model,
                    notes=note_map.get(session["uid"], []),
                    action_items=action_map.get(session["uid"], []),
                )
            )

        return timeline

    async def add_note(
        self,
        *,
        session_uid: UUID,
        author_uid: UUID,
        request: OneOnOneNoteRequest,
    ) -> OneOnOneNoteResponse:
        row = await self.conn.fetchrow(
            """
            INSERT INTO people.one_on_one_notes (
                session_uid,
                author_uid,
                visibility,
                content
            ) VALUES ($1, $2, $3, $4)
            RETURNING uid,
                      session_uid,
                      author_uid,
                      visibility,
                      content,
                      created_at;
            """,
            session_uid,
            author_uid,
            request.visibility.value,
            request.content,
        )
        note = OneOnOneNoteResponse.model_validate(dict(row))
        await log_audit_event(
            self.conn,
            entity_type="OneOnOneNote",
            entity_uid=note.uid,
            action="CREATE",
            performed_by=author_uid,
            after=dict(row),
        )
        return note

    async def add_action_item(
        self,
        *,
        request: ActionItemRequest,
    ) -> ActionItemResponse:
        row = await self.conn.fetchrow(
            """
            INSERT INTO people.action_items (
                session_uid,
                employee_uid,
                description,
                owner_uid,
                due_date,
                status
            ) VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING uid,
                      session_uid,
                      employee_uid,
                      description,
                      owner_uid,
                      due_date,
                      status,
                      created_at,
                      updated_at;
            """,
            request.session_uid,
            request.employee_uid,
            request.description,
            request.owner_uid,
            request.due_date,
            request.status.value,
        )
        action = ActionItemResponse.model_validate(dict(row))
        await log_audit_event(
            self.conn,
            entity_type="ActionItem",
            entity_uid=action.uid,
            action="CREATE",
            performed_by=action.owner_uid,
            after=dict(row),
        )
        return action

    async def update_action_item_status(
        self, *, action_uid: UUID, request: ActionItemStatusUpdate
    ) -> ActionItemResponse | None:
        row = await self.conn.fetchrow(
            """
            UPDATE people.action_items
            SET status = $2,
                updated_at = now()
            WHERE uid = $1
            RETURNING uid,
                      session_uid,
                      employee_uid,
                      description,
                      owner_uid,
                      due_date,
                      status,
                      created_at,
                      updated_at;
            """,
            action_uid,
            request.status.value,
        )
        if not row:
            return None
        action = ActionItemResponse.model_validate(dict(row))
        await log_audit_event(
            self.conn,
            entity_type="ActionItem",
            entity_uid=action.uid,
            action="UPDATE_STATUS",
            performed_by=action.owner_uid,
            after=dict(row),
        )
        return action

