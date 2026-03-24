from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now

if TYPE_CHECKING:
    from .project import Project
    from .user import User


class ProjectRole(StrEnum):
    OWNER = "owner"
    MANAGER = "manager"
    CONTRIBUTOR = "contributor"
    REVIEWER = "reviewer"


class ProjectMember(Base):
    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint(
            "id_project", "id_user", name="uq_project_members_project_user"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    id_project: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    id_user: Mapped[int] = mapped_column(ForeignKey("users.id"))
    role: Mapped[str] = mapped_column(String(32), default="reviewer")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now
    )

    project: Mapped[Project] = relationship("Project", back_populates="members")
    user: Mapped[User] = relationship("User", back_populates="project_memberships")
