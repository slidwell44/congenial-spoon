import typing as t
from datetime import datetime, UTC
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    uid: t.Annotated[UUID, Field(title="Unique Id")]
    id: t.Annotated[str, Field(title="User Id")]
    first_name: t.Annotated[str, Field(title="First Name")]
    last_name: t.Annotated[str, Field(title="Last Name")]
    email: t.Annotated[EmailStr, Field(title="Email")]
    created_at: t.Annotated[
        datetime, Field(default_factory=datetime.now(UTC), title="Created At")
    ]
