from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from .test_case import TestCase


class TestStep(Base):
    __tablename__ = "test_steps"
    __test__ = False

    id: Mapped[int] = mapped_column(primary_key=True)
    id_test_case: Mapped[int] = mapped_column(ForeignKey("test_cases.id"))
    order_num: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(500))
    expected_result: Mapped[str | None] = mapped_column(Text, nullable=True)

    test_case: Mapped[TestCase] = relationship("TestCase", back_populates="steps")
