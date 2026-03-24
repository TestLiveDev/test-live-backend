from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.project import ProjectRead


class TestPlanBase(BaseModel):
    name: str
    description: str | None = None


class TestPlanCreate(TestPlanBase):
    id_project: int


class TestPlanUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class TestPlanRead(TestPlanBase):
    id: int
    id_project: int
    project: ProjectRead | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
