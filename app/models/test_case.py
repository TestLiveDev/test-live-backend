from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now

if TYPE_CHECKING:
    from .release_test_case import ReleaseTestCase
    from .status import Status
    from .test_plan import TestPlan
    from .test_result import TestResult
    from .test_step import TestStep


class TestCase(Base):
    __tablename__ = "test_cases"
    __test__ = False

    id: Mapped[int] = mapped_column(primary_key=True)
    id_test_plan: Mapped[int] = mapped_column(ForeignKey("test_plans.id"))
    id_priority: Mapped[int] = mapped_column(ForeignKey("statuses.id"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    preconditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    postconditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now
    )

    test_plan: Mapped[TestPlan] = relationship("TestPlan", back_populates="test_cases")
    priority: Mapped[Status] = relationship(
        "Status", back_populates="test_cases_priority", foreign_keys=[id_priority]
    )
    steps: Mapped[list[TestStep]] = relationship(
        "TestStep",
        back_populates="test_case",
        cascade="all, delete-orphan",
        order_by="TestStep.order_num",
    )
    release_test_cases: Mapped[list[ReleaseTestCase]] = relationship(
        "ReleaseTestCase", back_populates="test_case", cascade="all, delete-orphan"
    )
    results: Mapped[list[TestResult]] = relationship(
        "TestResult", back_populates="test_case", cascade="all, delete-orphan"
    )
