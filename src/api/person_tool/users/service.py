from uuid import UUID

from asyncpg import Connection
from fastapi import status
from fastapi.exceptions import HTTPException

from person_tool.users.models import CreateUserRequest, UserResponse, UpdateUserRequest
from person_tool.users.repository import UserRepository


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
        response: list[UserResponse] = await self.repository.create_users(
            conn=conn, data=data
        )
        return response

    async def update_user(
        self, conn: Connection, data: UpdateUserRequest
    ) -> UserResponse:
        user: UserResponse | None = await self.repository.update_user(
            conn=conn, data=data
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with uid: {data.uid} not found",
            )
        return user

    async def delete_user(self, conn: Connection, uid: UUID) -> None:
        result: str = await self.repository.delete_user(conn=conn, uid=uid)
        if result != "DELETE 1":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with uid: {uid} not found",
            )
