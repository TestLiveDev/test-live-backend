from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TestResultAttachmentRead(BaseModel):
    id: int
    id_test_result: int
    original_name: str
    content_type: str | None = None
    size_bytes: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TestResultAttachmentDownloadRead(BaseModel):
    url: str
    expires_in_seconds: int
