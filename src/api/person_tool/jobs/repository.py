import json
from uuid import UUID

from asyncpg import Connection  # type: ignore
from asyncpg.protocol.protocol import Record  # type: ignore
from black.rusty import Result

from person_tool.jobs.models import JobResponse, CreateJobRequest, UpdateJobRequest


class JobRepository:
    def __init__(self):
        pass

    @staticmethod
    async def get_jobs(
        conn: Connection,
        *,
        job_id: str | None,
        title: str | None,
        status: str | None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[JobResponse] | None:
        result: list[Record] = await conn.fetch(
            """
            SELECT uid, id, title, description, status, created_at
            FROM people.jobs
            WHERE ($1::text IS NULL OR id ILIKE '%' || $1 || '%')
              AND ($2::text IS NULL OR title ILIKE '%' || $2 || '%')
              AND ($3::text IS NULL OR status ILIKE '%' || $3 || '%')
            ORDER BY created_at DESC
            LIMIT $4 OFFSET $5
            """,
            job_id,
            title,
            status,
            limit,
            offset,
        )
        if not result:
            return None
        return [JobResponse.model_validate(dict(r)) for r in result]

    @staticmethod
    async def get_job_by_id(conn: Connection, uid: UUID) -> JobResponse | None:
        result: Record | None = await conn.fetchrow(
            """
            SELECT uid, id, title, description, status, created_at
            FROM people.jobs WHERE uid = $1
            """,
            uid,
        )
        return JobResponse.model_validate(dict(result)) if result else None

    @staticmethod
    async def create_jobs(
        conn: Connection,
        data: list[CreateJobRequest],
    ) -> list[JobResponse]:
        payload: str = json.dumps([d.model_dump() for d in data])
        result: list[Record] = await conn.fetch(
            """
                WITH payload AS (
                    SELECT * FROM jsonb_to_recordset($1::jsonb)
                AS t(id text, title text, description text, status text)
                )
                INSERT INTO people.jobs (id, title, description, status)
                SELECT id, title, description, status
                FROM payload
                RETURNING uid, id, title, description, status, created_at;
                """,
            payload,
        )
        return [JobResponse.model_validate(dict(r)) for r in result]

    @staticmethod
    async def update_job(
        conn: Connection, data: UpdateJobRequest
    ) -> JobResponse | None:
        row: Record | None = await conn.fetchrow(
            """
            UPDATE people.jobs
            SET
                id          = COALESCE($2, id),
                title       = COALESCE($3, title),
                description = COALESCE($4, description),
                status      = COALESCE($5, status)
            WHERE uid = $1
            RETURNING uid, id, title, description, status, created_at;
            """,
            data.uid,
            data.id,
            data.title,
            data.description,
            data.status,
        )
        return JobResponse.model_validate(dict(row)) if row else None

    @staticmethod
    async def delete_job(conn: Connection, uid: UUID) -> str:
        result = await conn.execute(
            """
            DELETE FROM people.jobs WHERE uid = $1
            """,
            uid,
        )
        return result