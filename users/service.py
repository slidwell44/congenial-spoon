from uuid import UUID

from asyncpg import Connection  # type: ignore
from fastapi import status
from fastapi.exceptions import HTTPException

from users.models import CreateUserRequest, UserResponse
from users.repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_users(
        self,
        conn: Connection,
        *,
        user_id: str | None,
        first_name: str | None,
        last_name: str | None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[UserResponse]:
        users: list[UserResponse] | None = await self.repository.get_users(
            conn=conn,
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            limit=limit,
            offset=offset,
        )
        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Users not found",
            )
        return users

    async def get_user_by_id(self, conn: Connection, uid: UUID) -> UserResponse:
        user: UserResponse | None = await self.repository.get_user_by_id(
            conn=conn, uid=uid
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with uid: {uid} not found",
            )
        return user

    async def create_users(
        self, conn: Connection, data: list[CreateUserRequest]
    ) -> list[UserResponse]:
        conn.transaction().start()
        response: list[UserResponse] = await self.repository.create_users(
            conn=conn, data=data
        )
        conn.transaction().commit()
        return response

    async def delete_user(self, conn: Connection, user_id: str) -> None:
        conn.transaction().start()
        await self.repository.delete_user(conn=conn, user_id=user_id)
        conn.transaction().commit()
