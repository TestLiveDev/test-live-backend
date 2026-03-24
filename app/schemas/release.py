from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.project import ProjectRead
from app.schemas.status import StatusRead


class ReleaseBase(BaseModel):
    name: str
    description: str | None = None


class ReleaseCreate(ReleaseBase):
    id_project: int


class ReleaseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    id_status: int | None = None


class ReleaseRead(ReleaseBase):
    id: int
    id_project: int
    id_status: int
    project: ProjectRead | None = None
    status: StatusRead | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
