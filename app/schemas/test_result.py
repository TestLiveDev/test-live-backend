from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.status import StatusRead
from app.schemas.test_result_attachment import TestResultAttachmentRead


class TestResultBase(BaseModel):
    id_test_case: int
    id_release: int
    id_status: int
    comment: str | None = None
    executed_by: str | None = None


class TestResultCreate(TestResultBase):
    pass


class TestResultUpdate(BaseModel):
    id_status: int | None = None
    comment: str | None = None
    executed_by: str | None = None


class TestResultRead(TestResultBase):
    id: int
    executed_at: datetime
    status: StatusRead | None = None
    attachments: list[TestResultAttachmentRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
