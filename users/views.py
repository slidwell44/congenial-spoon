import typing as t
from uuid import UUID

from asyncpg import Connection  # type: ignore
from fastapi import APIRouter, Depends, Body, status, Path, Query
from fastapi.exceptions import HTTPException

from dependencies import (
    get_database_connection,
    get_user_service,
    get_database_transaction,
)
from users.models import CreateUserRequest, UserResponse, UpdateUserRequest
from users.service import UserService

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
    service: t.Annotated[UserService, Depends(get_user_service)],
    conn: t.Annotated[Connection, Depends(get_database_connection)],
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
    return await service.get_users(
        conn=conn,
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        limit=limit,
        offset=offset,
    )


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
    service: t.Annotated[UserService, Depends(get_user_service)],
    conn: t.Annotated[Connection, Depends(get_database_connection)],
    uid: UUID = Path(..., title="User id to retrieve"),
) -> UserResponse:
    """
    Retrieve a user by id
    """
    return await service.get_user_by_id(conn=conn, uid=uid)


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
    service: t.Annotated[UserService, Depends(get_user_service)],
    conn: t.Annotated[Connection, Depends(get_database_transaction)],
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
    return await service.create_users(conn=conn, data=data)


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
    service: t.Annotated[UserService, Depends(get_user_service)],
    conn: t.Annotated[Connection, Depends(get_database_transaction)],
    data: UpdateUserRequest = Body(...),
) -> UserResponse:
    """
    Update a user
    """
    user: UserResponse = await service.update_user(conn=conn, data=data)
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
    service: t.Annotated[UserService, Depends(get_user_service)],
    conn: t.Annotated[Connection, Depends(get_database_transaction)],
    uid: UUID = Path(..., title="User id to delete"),
) -> None:
    """
    Delete a user by uid
    """
    await service.delete_user(conn=conn, uid=uid)
