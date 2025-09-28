import typing as t
from uuid import UUID

from asyncpg import Connection  # type: ignore
from fastapi import APIRouter, Depends, Body, status, Path, Query
from fastapi.exceptions import HTTPException

from person_tool.dependencies import (
    get_database_connection,
    get_job_service,
    get_database_transaction,
)
from person_tool.jobs.models import CreateJobRequest, JobResponse, UpdateJobRequest
from person_tool.jobs.service import JobService

router = APIRouter()


@router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    summary="Get jobs by query params",
    responses={
        status.HTTP_200_OK: {
            "model": list[JobResponse],
            "description": "Gets jobs from the db by query parameters",
        },
        status.HTTP_404_NOT_FOUND: {"description": "Jobs not found"},
    },
)
async def get_jobs(
    service: t.Annotated[JobService, Depends(get_job_service)],
    conn: t.Annotated[Connection, Depends(get_database_connection)],
    job_id: t.Optional[str] = Query(
        default=None, alias="jobId", examples=["eng-001", "eng", "001"]
    ),
    title: t.Optional[str] = Query(
        default=None, examples=["engineer", "software", "developer"]
    ),
    job_status: t.Optional[str] = Query(
        default=None, alias="status", examples=["active", "inactive", "pending"]
    ),
    limit: int = 10,
    offset: int = 0,
) -> list[JobResponse]:
    """
    Get jobs by query params
    """
    return await service.get_jobs(
        conn=conn,
        job_id=job_id,
        title=title,
        job_status=job_status,
        limit=limit,
        offset=offset,
    )


@router.get(
    path="/{uid}",
    status_code=status.HTTP_200_OK,
    summary="Get job by uid",
    responses={
        status.HTTP_200_OK: {
            "model": JobResponse,
            "description": "Gets a job from the db by uid",
        },
        status.HTTP_404_NOT_FOUND: {"description": "Job not found"},
    },
)
async def get_job_by_id(
    service: t.Annotated[JobService, Depends(get_job_service)],
    conn: t.Annotated[Connection, Depends(get_database_connection)],
    uid: UUID = Path(..., title="Job id to retrieve"),
) -> JobResponse:
    """
    Retrieve a job by id
    """
    return await service.get_job_by_id(conn=conn, uid=uid)


@router.post(
    path="/",
    response_model=list[JobResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create jobs",
    responses={
        status.HTTP_201_CREATED: {
            "model": list[JobResponse],
            "description": "Creates jobs from the list of CreateJobRequests",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Cannot create more than 50 jobs at once"
        },
    },
)
async def create_jobs(
    service: t.Annotated[JobService, Depends(get_job_service)],
    conn: t.Annotated[Connection, Depends(get_database_transaction)],
    data: list[CreateJobRequest] = Body(..., title="List of jobs to create"),
) -> list[JobResponse]:
    """
    Create up to 50 jobs at a time
    """
    if len(data) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create more than 50 jobs at once",
        )
    return await service.create_jobs(conn=conn, data=data)


@router.patch(
    path="/",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: {
            "model": JobResponse,
            "description": "Job updated",
        },
        status.HTTP_404_NOT_FOUND: {"description": "Job not found"},
    },
)
async def update_job(
    service: t.Annotated[JobService, Depends(get_job_service)],
    conn: t.Annotated[Connection, Depends(get_database_transaction)],
    data: UpdateJobRequest = Body(...),
) -> JobResponse:
    """
    Update a job
    """
    job: JobResponse = await service.update_job(conn=conn, data=data)
    return job


@router.delete(
    path="/{uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a job by uid",
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Job deleted",
        },
        status.HTTP_404_NOT_FOUND: {"description": "Job not found"},
    },
)
async def delete_job(
    service: t.Annotated[JobService, Depends(get_job_service)],
    conn: t.Annotated[Connection, Depends(get_database_transaction)],
    uid: UUID = Path(..., title="Job id to delete"),
) -> None:
    """
    Delete a job by uid
    """
    await service.delete_job(conn=conn, uid=uid)