from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now

if TYPE_CHECKING:
    from .project import Project
    from .release_test_case import ReleaseTestCase
    from .release_test_plan import ReleaseTestPlan
    from .status import Status
    from .test_result import TestResult


class Release(Base):
    __tablename__ = "releases"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_project: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    id_status: Mapped[int] = mapped_column(ForeignKey("statuses.id"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now
    )

    project: Mapped[Project] = relationship("Project", back_populates="releases")
    status: Mapped[Status] = relationship(
        "Status", back_populates="releases", foreign_keys=[id_status]
    )
    release_test_plans: Mapped[list[ReleaseTestPlan]] = relationship(
        "ReleaseTestPlan", back_populates="release", cascade="all, delete-orphan"
    )
    release_test_cases: Mapped[list[ReleaseTestCase]] = relationship(
        "ReleaseTestCase", back_populates="release", cascade="all, delete-orphan"
    )
    test_results: Mapped[list[TestResult]] = relationship(
        "TestResult", back_populates="release", cascade="all, delete-orphan"
    )
