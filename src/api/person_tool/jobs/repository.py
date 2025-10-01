import json
from uuid import UUID

from asyncpg import Connection  # type: ignore
from asyncpg.protocol.protocol import Record  # type: ignore

from person_tool.jobs.models import CreateJobRequest, JobResponse, UpdateJobRequest


class JobRepository:
    def __init__(self, conn: Connection) -> None:
        self.conn: Connection = conn

    async def get_jobs(
        self,
        *,
        job_id: str | None,
        title: str | None,
        status: str | None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[JobResponse] | None:
        result: list[Record] = await self.conn.fetch(
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

    async def get_job_by_id(self, uid: UUID) -> JobResponse | None:
        result: Record | None = await self.conn.fetchrow(
            """
            SELECT uid, id, title, description, status, created_at
            FROM people.jobs WHERE uid = $1
            """,
            uid,
        )
        return JobResponse.model_validate(dict(result)) if result else None

    async def create_jobs(
        self,
        data: list[CreateJobRequest],
    ) -> list[JobResponse]:
        payload: str = json.dumps([d.model_dump() for d in data])
        result: list[Record] = await self.conn.fetch(
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

    async def update_job(self, data: UpdateJobRequest) -> JobResponse | None:
        row: Record | None = await self.conn.fetchrow(
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

    async def delete_job(self, uid: UUID) -> str:
        result = await self.conn.execute(
            """
            DELETE FROM people.jobs WHERE uid = $1
            """,
            uid,
        )
        return result
