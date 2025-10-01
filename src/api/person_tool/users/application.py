from uuid import UUID

from person_tool.factories.service_factory import service_factory
from person_tool.users.models import CreateUserRequest, UpdateUserRequest, UserResponse


class UserApplication:
    def __init__(self) -> None:
        self.service_factory = service_factory

    async def get_users(
        self,
        *,
        user_id: str | None,
        first_name: str | None,
        last_name: str | None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[UserResponse]:
        async with self.service_factory(use_transaction=False) as sf:
            users: list[UserResponse] = await sf.user_service.get_users(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                limit=limit,
                offset=offset,
            )
        return users

    async def get_user_by_id(self, uid: UUID) -> UserResponse:
        async with self.service_factory(use_transaction=False) as sf:
            user: UserResponse = await sf.user_service.get_user_by_id(uid=uid)
        return user

    async def create_users(self, data: list[CreateUserRequest]) -> list[UserResponse]:
        async with self.service_factory(use_transaction=True) as sf:
            users: list[UserResponse] = await sf.user_service.create_users(data=data)
        return users

    async def update_user(self, data: UpdateUserRequest) -> UserResponse:
        async with self.service_factory(use_transaction=True) as sf:
            user: UserResponse = await sf.user_service.update_user(data=data)
        return user

    async def delete_user(self, uid: UUID) -> None:
        async with self.service_factory(use_transaction=True) as sf:
            await sf.user_service.delete_user(uid=uid)
