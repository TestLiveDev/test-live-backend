from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now

if TYPE_CHECKING:
    from .test_result import TestResult


class TestResultAttachment(Base):
    __tablename__ = "test_result_attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_test_result: Mapped[int] = mapped_column(ForeignKey("test_results.id"))
    id_project: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    id_uploaded_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    bucket: Mapped[str] = mapped_column(String(255))
    object_key: Mapped[str] = mapped_column(String(1024), unique=True)
    original_name: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    size_bytes: Mapped[int] = mapped_column()
    etag: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    test_result: Mapped[TestResult] = relationship(
        "TestResult", back_populates="attachments"
    )
