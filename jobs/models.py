from uuid import UUID
from pydantic import BaseModel, Field  # type: ignore


class JobBase(BaseModel):
    title: str = Field()


class CreateJobRequest(JobBase):
    pass


class UpdateJobRequest(JobBase):
    uid: UUID
