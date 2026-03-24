from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from .release import Release
    from .test_case import TestCase
    from .test_result import TestResult


class Status(Base):
    __tablename__ = "statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(50))

    releases: Mapped[list[Release]] = relationship(
        "Release", back_populates="status", foreign_keys="Release.id_status"
    )
    test_cases_priority: Mapped[list[TestCase]] = relationship(
        "TestCase", back_populates="priority", foreign_keys="TestCase.id_priority"
    )
    test_results: Mapped[list[TestResult]] = relationship(
        "TestResult", back_populates="status", foreign_keys="TestResult.id_status"
    )
