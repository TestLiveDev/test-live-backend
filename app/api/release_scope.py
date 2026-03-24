# ruff: noqa: B008

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.release_assignment import ReleaseTestCaseAssign, ReleaseTestPlanAssign
from app.schemas.release_scope import ReleaseScopeRead
from app.security import DELETE_ROLES, READ_ROLES, WRITE_ROLES, get_current_user
from app.services.release_scope_service import (
    add_test_case_to_release_scope,
    add_test_plan_to_release_scope,
    build_release_scope,
    remove_test_case_from_release_scope,
    remove_test_plan_from_release_scope,
)

router = APIRouter(prefix="/api/releases", tags=["release-scope"])


@router.get("/{release_id}/scope", response_model=ReleaseScopeRead)
async def get_release_scope(
    release_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await build_release_scope(db, current_user, release_id, READ_ROLES)


@router.post(
    "/{release_id}/test-cases",
    response_model=ReleaseScopeRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_test_case_to_release(
    release_id: int,
    payload: ReleaseTestCaseAssign,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await add_test_case_to_release_scope(
        db,
        current_user,
        release_id,
        payload,
        WRITE_ROLES,
    )


@router.post(
    "/{release_id}/test-plans",
    response_model=ReleaseScopeRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_test_plan_to_release(
    release_id: int,
    payload: ReleaseTestPlanAssign,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await add_test_plan_to_release_scope(
        db,
        current_user,
        release_id,
        payload,
        WRITE_ROLES,
    )


@router.delete(
    "/{release_id}/test-cases/{test_case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_test_case_from_release(
    release_id: int,
    test_case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await remove_test_case_from_release_scope(
        db,
        current_user,
        release_id,
        test_case_id,
        DELETE_ROLES,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/{release_id}/test-plans/{test_plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_test_plan_from_release(
    release_id: int,
    test_plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await remove_test_plan_from_release_scope(
        db,
        current_user,
        release_id,
        test_plan_id,
        DELETE_ROLES,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
