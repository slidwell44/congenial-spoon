from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict  # type: ignore
from pydantic.alias_generators import to_camel


class JobBase(BaseModel):
    title: str = Field(min_length=1, max_length=200, examples=["Software Engineer"])
    description: str = Field(min_length=1, examples=["Develop and maintain software applications."])

    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )


class CreateJobRequest(JobBase):
    pass


class UpdateJobRequest(BaseModel):
    uid: UUID
    title: str | None = Field(default=None)
    description: str | None = Field(default=None)
    
    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )
    
class JobResponse(JobBase):
    uid: UUID
    created_at: datetime
