import json
from uuid import UUID

from asyncpg import Connection  # type: ignore

from users.models import UserResponse, CreateUserRequest


class UserRepository:
    def __init__(self):
        pass

    @staticmethod
    async def get_users(conn: Connection, user_id: str) -> list[UserResponse] | None:
        result = await conn.fetchrow(
            """
            SELECT uid, id, first_name, last_name, email, created_at
            FROM people.users WHERE id = $1
            """,
            user_id,
        )
        if not result:
            return None
        # TODO 9/21/2025: Handle query params that return multiple results
        return [UserResponse.model_validate(dict(result))]

    @staticmethod
    async def get_user_by_id(conn: Connection, uid: UUID) -> UserResponse | None:
        result = await conn.fetchrow(
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
        result = await conn.execute(
            """
                WITH payload AS (
                    SELECT * FROM jsonb_to_recordset($1::jsonb)
                AS t(id text, first_name text, last_name text, email text)
                )
                INSERT INTO people.users (id, first_name, last_name, email)
                SELECT id, first_name, last_name, email
                FROM payload
                RETURNING uid, id, first_name, last_name, email, created_at
                """,
            json.dumps([d.model_dump() for d in data]),
        )

        return [UserResponse.model_validate(r) for r in result]

    @staticmethod
    async def delete_user(conn: Connection, user_id: str) -> None:
        result = await conn.execute(
            """
            DELETE FROM people.users WHERE uid = $1
            """,
            user_id,
        )
        print(result)
