from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.status import StatusRead


class TestCaseBase(BaseModel):
    name: str
    description: str | None = None
    preconditions: str | None = None
    postconditions: str | None = None


class TestCaseCreate(TestCaseBase):
    id_test_plan: int
    id_priority: int | None = None


class TestCaseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    preconditions: str | None = None
    postconditions: str | None = None
    id_priority: int | None = None


class TestCaseRead(TestCaseBase):
    id: int
    id_test_plan: int
    id_priority: int
    priority: StatusRead | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
