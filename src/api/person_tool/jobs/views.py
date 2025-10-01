import typing as t
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Query, status
from fastapi.exceptions import HTTPException

from person_tool.dependencies import provide_job_application
from person_tool.jobs.application import JobApplication
from person_tool.jobs.models import CreateJobRequest, JobResponse, UpdateJobRequest

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
    application: t.Annotated[JobApplication, Depends(provide_job_application)],
    job_id: str | None = Query(
        default=None, alias="jobId", examples=["eng-001", "eng", "001"]
    ),
    title: str | None = Query(
        default=None, examples=["engineer", "software", "developer"]
    ),
    job_status: str | None = Query(
        default=None, alias="status", examples=["active", "inactive", "pending"]
    ),
    limit: int = 10,
    offset: int = 0,
) -> list[JobResponse]:
    """
    Get jobs by query params
    """
    return await application.get_jobs(
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
    application: t.Annotated[JobApplication, Depends(provide_job_application)],
    uid: UUID = Path(..., title="Job id to retrieve"),
) -> JobResponse:
    """
    Retrieve a job by id
    """
    return await application.get_job_by_id(uid=uid)


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
    application: t.Annotated[JobApplication, Depends(provide_job_application)],
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
    return await application.create_jobs(data=data)


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
    application: t.Annotated[JobApplication, Depends(provide_job_application)],
    data: UpdateJobRequest = Body(...),
) -> JobResponse:
    """
    Update a job
    """
    job: JobResponse = await application.update_job(data=data)
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
    application: t.Annotated[JobApplication, Depends(provide_job_application)],
    uid: UUID = Path(..., title="Job id to delete"),
) -> None:
    """
    Delete a job by uid
    """
    await application.delete_job(uid=uid)
