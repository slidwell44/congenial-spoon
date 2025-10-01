from uuid import UUID

from person_tool.factories.service_factory import service_factory
from person_tool.jobs.models import CreateJobRequest, JobResponse, UpdateJobRequest


class JobApplication:
    def __init__(self) -> None:
        self.service_factory = service_factory

    async def get_jobs(
        self,
        *,
        job_id: str | None,
        title: str | None,
        job_status: str | None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[JobResponse]:
        async with self.service_factory(use_transaction=False) as sf:
            jobs: list[JobResponse] = await sf.jobs_service.get_jobs(
                job_id=job_id,
                title=title,
                job_status=job_status,
                limit=limit,
                offset=offset,
            )
        return jobs

    async def get_job_by_id(self, uid: UUID) -> JobResponse:
        async with self.service_factory(use_transaction=False) as sf:
            job: JobResponse = await sf.jobs_service.get_job_by_id(uid=uid)
        return job

    async def create_jobs(self, data: list[CreateJobRequest]) -> list[JobResponse]:
        async with self.service_factory(use_transaction=True) as sf:
            jobs: list[JobResponse] = await sf.jobs_service.create_jobs(data=data)
        return jobs

    async def update_job(self, data: UpdateJobRequest) -> JobResponse:
        async with self.service_factory(use_transaction=True) as sf:
            job: JobResponse = await sf.jobs_service.update_job(data=data)
        return job

    async def delete_job(self, uid: UUID) -> None:
        async with self.service_factory(use_transaction=True) as sf:
            await sf.jobs_service.delete_job(uid=uid)
