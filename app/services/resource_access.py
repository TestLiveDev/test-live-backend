from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project, Release, TestCase, TestPlan, TestResult, User
from app.security import require_project_roles


def _not_found(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


async def _get_by_id_or_404(
    db: AsyncSession,
    model: type[Any],
    object_id: int,
    detail: str,
    *options: Any,
) -> Any:
    query = select(model).where(model.id == object_id)
    if options:
        query = query.options(*options)

    result = await db.execute(query)
    instance = result.scalar_one_or_none()
    if instance is None:
        raise _not_found(detail)
    return instance


async def get_project_or_404(
    db: AsyncSession,
    project_id: int,
    *options: Any,
) -> Project:
    return await _get_by_id_or_404(
        db, Project, project_id, "Project not found", *options
    )


async def get_release_or_404(
    db: AsyncSession,
    release_id: int,
    *options: Any,
) -> Release:
    return await _get_by_id_or_404(
        db, Release, release_id, "Release not found", *options
    )


async def get_test_plan_or_404(
    db: AsyncSession,
    test_plan_id: int,
    *options: Any,
) -> TestPlan:
    return await _get_by_id_or_404(
        db,
        TestPlan,
        test_plan_id,
        "TestPlan not found",
        *options,
    )


async def get_test_case_or_404(
    db: AsyncSession,
    test_case_id: int,
    *options: Any,
) -> TestCase:
    return await _get_by_id_or_404(
        db,
        TestCase,
        test_case_id,
        "TestCase not found",
        *options,
    )


async def get_test_result_or_404(
    db: AsyncSession,
    result_id: int,
    *options: Any,
) -> TestResult:
    return await _get_by_id_or_404(
        db, TestResult, result_id, "Result not found", *options
    )


async def get_project_for_roles(
    db: AsyncSession,
    current_user: User,
    project_id: int,
    allowed_roles: set[str],
    *options: Any,
) -> Project:
    project = await get_project_or_404(db, project_id, *options)
    await require_project_roles(db, current_user, project.id, allowed_roles)
    return project


async def get_release_for_roles(
    db: AsyncSession,
    current_user: User,
    release_id: int,
    allowed_roles: set[str],
    *options: Any,
) -> Release:
    release = await get_release_or_404(db, release_id, *options)
    await require_project_roles(db, current_user, release.id_project, allowed_roles)
    return release


async def get_test_plan_for_roles(
    db: AsyncSession,
    current_user: User,
    test_plan_id: int,
    allowed_roles: set[str],
    *options: Any,
) -> TestPlan:
    test_plan = await get_test_plan_or_404(db, test_plan_id, *options)
    await require_project_roles(db, current_user, test_plan.id_project, allowed_roles)
    return test_plan


async def get_test_case_for_roles(
    db: AsyncSession,
    current_user: User,
    test_case_id: int,
    allowed_roles: set[str],
    *options: Any,
) -> TestCase:
    test_case = await get_test_case_or_404(db, test_case_id, *options)
    await require_project_roles(
        db, current_user, test_case.test_plan.id_project, allowed_roles
    )
    return test_case


async def get_test_result_for_roles(
    db: AsyncSession,
    current_user: User,
    result_id: int,
    allowed_roles: set[str],
    *options: Any,
) -> TestResult:
    test_result = await get_test_result_or_404(db, result_id, *options)
    await require_project_roles(
        db, current_user, test_result.release.id_project, allowed_roles
    )
    return test_result
