import json
from uuid import UUID

from asyncpg import Connection  # type: ignore
from asyncpg.protocol.protocol import Record  # type: ignore
from black.rusty import Result

from users.models import UserResponse, CreateUserRequest, UpdateUserRequest


class UserRepository:
    def __init__(self):
        pass

    @staticmethod
    async def get_users(
        conn: Connection,
        *,
        user_id: str | None,
        first_name: str | None,
        last_name: str | None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[UserResponse] | None:
        result: list[Record] = await conn.fetch(
            """
            SELECT uid, id, first_name, last_name, email, created_at
            FROM people.users
            WHERE ($1::text IS NULL OR id ILIKE '%' || $1 || '%')
              AND ($2::text IS NULL OR first_name ILIKE '%' || $2 || '%')
              AND ($3::text IS NULL OR last_name  ILIKE '%' || $3 || '%')
            ORDER BY created_at DESC
            LIMIT $4 OFFSET $5
            """,
            user_id,
            first_name,
            last_name,
            limit,
            offset,
        )
        if not result:
            return None
        return [UserResponse.model_validate(dict(r)) for r in result]

    @staticmethod
    async def get_user_by_id(conn: Connection, uid: UUID) -> UserResponse | None:
        result: Record = await conn.fetchrow(
            """
            SELECT uid, id, first_name, last_name, email, created_at
            FROM people.users WHERE uid = $1
            """,
            uid,
        )
        return UserResponse.model_validate(dict(result)) if result else None

    @staticmethod
    async def create_users(
        conn: Connection,
        data: list[CreateUserRequest],
    ) -> list[UserResponse]:
        payload: str = json.dumps([d.model_dump() for d in data])
        result: list[Record] = await conn.fetch(
            """
                WITH payload AS (
                    SELECT * FROM jsonb_to_recordset($1::jsonb)
                AS t(id text, first_name text, last_name text, email text)
                )
                INSERT INTO people.users (id, first_name, last_name, email)
                SELECT id, first_name, last_name, email
                FROM payload
                RETURNING uid, id, first_name, last_name, email, created_at;
                """,
            payload,
        )
        return [UserResponse.model_validate(dict(r)) for r in result]

    @staticmethod
    async def update_user(
        conn: Connection, data: UpdateUserRequest
    ) -> UserResponse | None:
        row: Record | None = await conn.fetchrow(
            """
            UPDATE people.users
            SET
                id         = COALESCE($2, id),
                first_name = COALESCE($3, first_name),
                last_name  = COALESCE($4, last_name),
                email      = COALESCE($5, email)
            WHERE uid = $1
            RETURNING uid, id, first_name, last_name, email, created_at;
            """,
            data.uid,
            data.id,
            data.first_name,
            data.last_name,
            data.email,
        )
        return UserResponse.model_validate(dict(row)) if row else None

    @staticmethod
    async def delete_user(conn: Connection, uid: UUID) -> str:
        result = await conn.execute(
            """
            DELETE FROM people.users WHERE uid = $1
            """,
            uid,
        )
        return result
