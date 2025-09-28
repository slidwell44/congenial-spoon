from uuid import UUID

from asyncpg import Connection
from fastapi import status
from fastapi.exceptions import HTTPException

from person_tool.jobs.models import CreateJobRequest, JobResponse, UpdateJobRequest
from person_tool.jobs.repository import JobRepository


class JobService:
    def __init__(self, repository: JobRepository):
        self.repository = repository

    async def get_jobs(
        self,
        conn: Connection,
        *,
        job_id: str | None,
        title: str | None,
        job_status: str | None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[JobResponse]:
        jobs: list[JobResponse] | None = await self.repository.get_jobs(
            conn=conn,
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

    async def get_job_by_id(self, conn: Connection, uid: UUID) -> JobResponse:
        job: JobResponse | None = await self.repository.get_job_by_id(
            conn=conn, uid=uid
        )
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with uid: {uid} not found",
            )
        return job

    async def create_jobs(
        self, conn: Connection, data: list[CreateJobRequest]
    ) -> list[JobResponse]:
        response: list[JobResponse] = await self.repository.create_jobs(
            conn=conn, data=data
        )
        return response

    async def update_job(
        self, conn: Connection, data: UpdateJobRequest
    ) -> JobResponse:
        job: JobResponse | None = await self.repository.update_job(
            conn=conn, data=data
        )
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with uid: {data.uid} not found",
            )
        return job

    async def delete_job(self, conn: Connection, uid: UUID) -> None:
        result: str = await self.repository.delete_job(conn=conn, uid=uid)
        if result != "DELETE 1":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with uid: {uid} not found",
            )