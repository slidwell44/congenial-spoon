from uuid import UUID

from fastapi import status
from fastapi.exceptions import HTTPException

from person_tool.jobs.models import CreateJobRequest, JobResponse, UpdateJobRequest
from person_tool.jobs.repository import JobRepository


class JobService:
    def __init__(self, repository: JobRepository):
        self.repository: JobRepository = repository

    async def get_jobs(
        self,
        *,
        job_id: str | None,
        title: str | None,
        job_status: str | None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[JobResponse]:
        jobs: list[JobResponse] | None = await self.repository.get_jobs(
            job_id=job_id,
            title=title,
            status=job_status,
            limit=limit,
            offset=offset,
        )
        if not jobs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Jobs not found",
            )
        return jobs

    async def get_job_by_id(self, uid: UUID) -> JobResponse:
        job: JobResponse | None = await self.repository.get_job_by_id(uid=uid)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with uid: {uid} not found",
            )
        return job

    async def create_jobs(self, data: list[CreateJobRequest]) -> list[JobResponse]:
        response: list[JobResponse] = await self.repository.create_jobs(data=data)
        return response

    async def update_job(self, data: UpdateJobRequest) -> JobResponse:
        job: JobResponse | None = await self.repository.update_job(data=data)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with uid: {data.uid} not found",
            )
        return job

    async def delete_job(self, uid: UUID) -> None:
        result: str = await self.repository.delete_job(uid=uid)
        if result != "DELETE 1":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with uid: {uid} not found",
            )
