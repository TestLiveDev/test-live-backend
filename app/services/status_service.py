from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Status

RELEASE_STATUS_CATEGORY = "release_priority"
TEST_CASE_PRIORITY_CATEGORY = "priority"
TEST_RESULT_STATUS_CATEGORY = "result"


async def get_status_by_code_and_category(
    db: AsyncSession,
    code: str,
    category: str,
) -> Status:
    result = await db.execute(
        select(Status).where(Status.code == code, Status.category == category)
    )
    status_record = result.scalar_one_or_none()
    if status_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Status '{code}' not found for category '{category}'",
        )
    return status_record


async def validate_status_category(
    db: AsyncSession,
    status_id: int,
    expected_category: str,
) -> Status:
    result = await db.execute(select(Status).where(Status.id == status_id))
    status_record = result.scalar_one_or_none()
    if status_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Status not found",
        )
    if status_record.category != expected_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status must belong to '{expected_category}' category",
        )
    return status_record
