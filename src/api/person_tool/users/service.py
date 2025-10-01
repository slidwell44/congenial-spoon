from uuid import UUID

from fastapi import status
from fastapi.exceptions import HTTPException

from person_tool.users.models import CreateUserRequest, UpdateUserRequest, UserResponse
from person_tool.users.repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_users(
        self,
        *,
        user_id: str | None,
        first_name: str | None,
        last_name: str | None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[UserResponse]:
        users: list[UserResponse] | None = await self.repository.get_users(
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

    async def get_user_by_id(self, uid: UUID) -> UserResponse:
        user: UserResponse | None = await self.repository.get_user_by_id(uid=uid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with uid: {uid} not found",
            )
        return user

    async def create_users(self, data: list[CreateUserRequest]) -> list[UserResponse]:
        response: list[UserResponse] = await self.repository.create_users(data=data)
        return response

    async def update_user(self, data: UpdateUserRequest) -> UserResponse:
        user: UserResponse | None = await self.repository.update_user(data=data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with uid: {data.uid} not found",
            )
        return user

    async def delete_user(self, uid: UUID) -> None:
        result: str = await self.repository.delete_user(uid=uid)
        if result != "DELETE 1":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with uid: {uid} not found",
            )
