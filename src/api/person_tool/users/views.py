import typing as t
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Query, status
from fastapi.exceptions import HTTPException

from person_tool.dependencies import provide_user_application
from person_tool.users.application import UserApplication
from person_tool.users.models import CreateUserRequest, UpdateUserRequest, UserResponse

router = APIRouter()


@router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    summary="Get users by query params",
    responses={
        status.HTTP_200_OK: {
            "model": list[UserResponse],
            "description": "Gets a user from the db by uid",
        },
        status.HTTP_404_NOT_FOUND: {"description": "Users not found"},
    },
)
async def get_users(
    application: t.Annotated[UserApplication, Depends(provide_user_application)],
    user_id: t.Optional[str] = Query(
        default=None, alias="userId", examples=["sl3789", "sl", "789"]
    ),
    first_name: t.Optional[str] = Query(
        default=None, alias="firstName", examples=["simon", "si", "mon"]
    ),
    last_name: t.Optional[str] = Query(
        default=None, alias="lastName", examples=["lidwell", "li", "ell"]
    ),
    limit: int = 10,
    offset: int = 0,
) -> list[UserResponse]:
    """
    Get users by query params
    """
    response: list[UserResponse] = await application.get_users(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        limit=limit,
        offset=offset,
    )
    return response


@router.get(
    path="/{uid}",
    status_code=status.HTTP_200_OK,
    summary="Get user by uid",
    responses={
        status.HTTP_200_OK: {
            "model": UserResponse,
            "description": "Gets a user from the db by uid",
        },
        status.HTTP_404_NOT_FOUND: {"description": "Users not found"},
    },
)
async def get_user_by_id(
    application: t.Annotated[UserApplication, Depends(provide_user_application)],
    uid: UUID = Path(..., title="User id to retrieve"),
) -> UserResponse:
    """
    Retrieve a user by id
    """
    response: UserResponse = await application.get_user_by_id(uid=uid)
    return response


@router.get(
    path="/{uid}/jobs",
    status_code=status.HTTP_200_OK,
    summary="Get a user with their jobs",
    responses={
        status.HTTP_200_OK: {
            "description": "Gets a user with all jobs attached to them"
        },
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    },
)
async def get_user_with_jobs_by_uid(
    application: t.Annotated[UserApplication, Depends(provide_user_application)],
):
    return NotImplementedError()


@router.post(
    path="/",
    response_model=list[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create users",
    responses={
        status.HTTP_201_CREATED: {
            "model": list[UserResponse],
            "description": "Creates users from the list of CreateUserRequests",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Cannot create more than 50 users at once"
        },
    },
)
async def create_users(
    application: t.Annotated[UserApplication, Depends(provide_user_application)],
    data: list[CreateUserRequest] = Body(..., title="List of users to create"),
) -> list[UserResponse]:
    """
    Create up to 50 users at a time
    """
    if len(data) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create more than 50 users at once",
        )
    return await application.create_users(data=data)


@router.patch(
    path="/",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: {
            "model": UserResponse,
            "description": "User updated",
        },
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    },
)
async def update_user(
    application: t.Annotated[UserApplication, Depends(provide_user_application)],
    data: UpdateUserRequest = Body(...),
) -> UserResponse:
    """
    Update a user
    """
    user: UserResponse = await application.update_user(data=data)
    return user


@router.delete(
    path="/{uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user by uid",
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "User deleted",
        },
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    },
)
async def delete_user(
    application: t.Annotated[UserApplication, Depends(provide_user_application)],
    uid: UUID = Path(..., title="User id to delete"),
) -> None:
    """
    Delete a user by uid
    """
    await application.delete_user(uid=uid)
