# ruff: noqa: B008

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Status
from app.schemas.status import StatusRead
from app.security import get_current_user

router = APIRouter(prefix="/api/statuses", tags=["statuses"])


@router.get("", response_model=list[StatusRead])
async def get_statuses(
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    query = select(Status)

    if category:
        query = query.where(Status.category == category)

    result = await db.execute(query.order_by(Status.id))
    return result.scalars().all()
