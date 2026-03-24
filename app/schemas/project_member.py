from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectMemberBase(BaseModel):
    role: str


class ProjectMemberCreate(ProjectMemberBase):
    email: str


class ProjectMemberUpdate(BaseModel):
    role: str


class ProjectMemberRead(BaseModel):
    id: int
    id_project: int
    id_user: int
    role: str
    created_at: datetime
    updated_at: datetime
    email: str
    full_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProjectMemberRoleRead(BaseModel):
    id_project: int
    id_user: int
    role: str
