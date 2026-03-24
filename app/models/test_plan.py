from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now

if TYPE_CHECKING:
    from .project import Project
    from .release_test_plan import ReleaseTestPlan
    from .test_case import TestCase


class TestPlan(Base):
    __tablename__ = "test_plans"
    __test__ = False

    id: Mapped[int] = mapped_column(primary_key=True)
    id_project: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now
    )

    project: Mapped[Project] = relationship("Project", back_populates="test_plans")
    release_test_plans: Mapped[list[ReleaseTestPlan]] = relationship(
        "ReleaseTestPlan", back_populates="test_plan", cascade="all, delete-orphan"
    )
    test_cases: Mapped[list[TestCase]] = relationship(
        "TestCase", back_populates="test_plan", cascade="all, delete-orphan"
    )
