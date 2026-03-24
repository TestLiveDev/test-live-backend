from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now

if TYPE_CHECKING:
    from .release import Release
    from .test_case import TestCase


class ReleaseTestCase(Base):
    __tablename__ = "release_test_cases"
    __table_args__ = (
        UniqueConstraint(
            "id_release",
            "id_test_case",
            name="uq_release_test_cases_release_case",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    id_release: Mapped[int] = mapped_column(ForeignKey("releases.id"))
    id_test_case: Mapped[int] = mapped_column(ForeignKey("test_cases.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    release: Mapped[Release] = relationship(
        "Release", back_populates="release_test_cases"
    )
    test_case: Mapped[TestCase] = relationship(
        "TestCase", back_populates="release_test_cases"
    )
