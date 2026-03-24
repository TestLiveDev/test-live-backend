from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now

if TYPE_CHECKING:
    from .release import Release
    from .status import Status
    from .test_case import TestCase
    from .test_result_attachment import TestResultAttachment


class TestResult(Base):
    __tablename__ = "test_results"
    __test__ = False

    id: Mapped[int] = mapped_column(primary_key=True)
    id_test_case: Mapped[int] = mapped_column(ForeignKey("test_cases.id"))
    id_release: Mapped[int] = mapped_column(ForeignKey("releases.id"))
    id_status: Mapped[int] = mapped_column(ForeignKey("statuses.id"))
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    executed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    test_case: Mapped[TestCase] = relationship("TestCase", back_populates="results")
    release: Mapped[Release] = relationship("Release", back_populates="test_results")
    status: Mapped[Status] = relationship("Status", back_populates="test_results")
    attachments: Mapped[list[TestResultAttachment]] = relationship(
        "TestResultAttachment",
        back_populates="test_result",
        cascade="all, delete-orphan",
        order_by="TestResultAttachment.created_at.desc()",
    )
