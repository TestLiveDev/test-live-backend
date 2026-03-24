from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Release,
    ReleaseTestCase,
    ReleaseTestPlan,
    TestCase,
    TestPlan,
    TestResult,
    User,
)
from app.schemas.release import ReleaseRead
from app.schemas.release_assignment import ReleaseTestCaseAssign, ReleaseTestPlanAssign
from app.schemas.release_scope import (
    ReleaseScopeCaseRead,
    ReleaseScopePlanRead,
    ReleaseScopeRead,
)
from app.schemas.status import StatusRead
from app.schemas.test_result import TestResultRead
from app.schemas.test_step import TestStepRead
from app.services.object_storage_service import (
    commit_staged_object_deletions,
    rollback_staged_object_deletions,
)
from app.services.resource_access import (
    get_release_for_roles,
    get_test_case_or_404,
    get_test_plan_or_404,
)
from app.services.test_result_service import stage_result_attachment_deletions


def empty_counts() -> dict[str, int]:
    return {
        "total_cases": 0,
        "passed": 0,
        "failed": 0,
        "blocked": 0,
        "skipped": 0,
        "not_run": 0,
    }


async def build_release_scope(
    db: AsyncSession,
    current_user: User,
    release_id: int,
    allowed_roles: set[str],
) -> ReleaseScopeRead:
    release = await get_release_for_roles(
        db,
        current_user,
        release_id,
        allowed_roles,
        selectinload(Release.project),
        selectinload(Release.status),
        selectinload(Release.release_test_plans).selectinload(
            ReleaseTestPlan.test_plan
        ),
        selectinload(Release.release_test_cases)
        .selectinload(ReleaseTestCase.test_case)
        .selectinload(TestCase.test_plan),
        selectinload(Release.release_test_cases)
        .selectinload(ReleaseTestCase.test_case)
        .selectinload(TestCase.priority),
        selectinload(Release.release_test_cases)
        .selectinload(ReleaseTestCase.test_case)
        .selectinload(TestCase.steps),
    )

    results_result = await db.execute(
        select(TestResult)
        .options(
            selectinload(TestResult.status),
            selectinload(TestResult.attachments),
        )
        .where(TestResult.id_release == release_id)
    )
    results_by_case = {
        result.id_test_case: result for result in results_result.scalars().all()
    }

    plans_map: dict[int, dict] = {}
    for release_test_plan in sorted(
        release.release_test_plans,
        key=lambda item: item.test_plan.name.lower(),
    ):
        test_plan = release_test_plan.test_plan
        plans_map[test_plan.id] = {
            "id": test_plan.id,
            "name": test_plan.name,
            "description": test_plan.description,
            **empty_counts(),
            "cases": [],
        }

    total_counts = empty_counts()

    for release_test_case in sorted(
        release.release_test_cases,
        key=lambda item: (
            item.test_case.test_plan.name.lower(),
            item.test_case.name.lower(),
            item.test_case.id,
        ),
    ):
        test_case = release_test_case.test_case
        test_plan = test_case.test_plan
        current_result = results_by_case.get(test_case.id)

        plan_entry = plans_map.setdefault(
            test_plan.id,
            {
                "id": test_plan.id,
                "name": test_plan.name,
                "description": test_plan.description,
                **empty_counts(),
                "cases": [],
            },
        )

        plan_entry["cases"].append(
            ReleaseScopeCaseRead(
                id=test_case.id,
                id_test_plan=test_case.id_test_plan,
                id_priority=test_case.id_priority,
                name=test_case.name,
                description=test_case.description,
                preconditions=test_case.preconditions,
                postconditions=test_case.postconditions,
                priority=StatusRead.model_validate(test_case.priority)
                if test_case.priority
                else None,
                steps=[TestStepRead.model_validate(step) for step in test_case.steps],
                result=TestResultRead.model_validate(current_result)
                if current_result
                else None,
            )
        )
        plan_entry["total_cases"] += 1
        total_counts["total_cases"] += 1

        status_code = (
            current_result.status.code
            if current_result and current_result.status
            else None
        )
        if status_code == "passed":
            plan_entry["passed"] += 1
            total_counts["passed"] += 1
        elif status_code == "failed":
            plan_entry["failed"] += 1
            total_counts["failed"] += 1
        elif status_code == "blocked":
            plan_entry["blocked"] += 1
            total_counts["blocked"] += 1
        elif status_code == "skipped":
            plan_entry["skipped"] += 1
            total_counts["skipped"] += 1
        else:
            plan_entry["not_run"] += 1
            total_counts["not_run"] += 1

    plans = [ReleaseScopePlanRead(**plan_data) for plan_data in plans_map.values()]
    pass_rate = (
        round(total_counts["passed"] / total_counts["total_cases"] * 100, 2)
        if total_counts["total_cases"]
        else 0.0
    )

    return ReleaseScopeRead(
        release=ReleaseRead.model_validate(release),
        pass_rate=pass_rate,
        plans=plans,
        **total_counts,
    )


async def add_test_case_to_release_scope(
    db: AsyncSession,
    current_user: User,
    release_id: int,
    payload: ReleaseTestCaseAssign,
    allowed_roles: set[str],
) -> ReleaseScopeRead:
    release = await get_release_for_roles(db, current_user, release_id, allowed_roles)
    test_case = await get_test_case_or_404(
        db,
        payload.id_test_case,
        selectinload(TestCase.test_plan),
    )
    if test_case.test_plan.id_project != release.id_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test case belongs to another project",
        )

    existing_case_result = await db.execute(
        select(ReleaseTestCase).where(
            ReleaseTestCase.id_release == release_id,
            ReleaseTestCase.id_test_case == payload.id_test_case,
        )
    )
    if existing_case_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Test case already added to release",
        )

    existing_plan_result = await db.execute(
        select(ReleaseTestPlan).where(
            ReleaseTestPlan.id_release == release_id,
            ReleaseTestPlan.id_test_plan == test_case.id_test_plan,
        )
    )
    if existing_plan_result.scalar_one_or_none() is None:
        db.add(
            ReleaseTestPlan(
                id_release=release_id,
                id_test_plan=test_case.id_test_plan,
            )
        )

    db.add(
        ReleaseTestCase(
            id_release=release_id,
            id_test_case=payload.id_test_case,
        )
    )
    await db.commit()
    return await build_release_scope(db, current_user, release_id, allowed_roles)


async def add_test_plan_to_release_scope(
    db: AsyncSession,
    current_user: User,
    release_id: int,
    payload: ReleaseTestPlanAssign,
    allowed_roles: set[str],
) -> ReleaseScopeRead:
    release = await get_release_for_roles(db, current_user, release_id, allowed_roles)
    test_plan = await get_test_plan_or_404(
        db,
        payload.id_test_plan,
        selectinload(TestPlan.test_cases),
    )
    if test_plan.id_project != release.id_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test plan belongs to another project",
        )

    existing_plan_result = await db.execute(
        select(ReleaseTestPlan).where(
            ReleaseTestPlan.id_release == release_id,
            ReleaseTestPlan.id_test_plan == payload.id_test_plan,
        )
    )
    if existing_plan_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Test plan already added to release",
        )

    db.add(
        ReleaseTestPlan(
            id_release=release_id,
            id_test_plan=payload.id_test_plan,
        )
    )

    existing_case_ids_result = await db.execute(
        select(ReleaseTestCase.id_test_case).where(
            ReleaseTestCase.id_release == release_id
        )
    )
    existing_case_ids = set(existing_case_ids_result.scalars().all())

    for test_case in test_plan.test_cases:
        if test_case.id in existing_case_ids:
            continue
        db.add(
            ReleaseTestCase(
                id_release=release_id,
                id_test_case=test_case.id,
            )
        )

    await db.commit()
    return await build_release_scope(db, current_user, release_id, allowed_roles)


async def remove_test_case_from_release_scope(
    db: AsyncSession,
    current_user: User,
    release_id: int,
    test_case_id: int,
    allowed_roles: set[str],
) -> None:
    await get_release_for_roles(db, current_user, release_id, allowed_roles)
    release_test_case_result = await db.execute(
        select(ReleaseTestCase)
        .options(selectinload(ReleaseTestCase.test_case))
        .where(
            ReleaseTestCase.id_release == release_id,
            ReleaseTestCase.id_test_case == test_case_id,
        )
    )
    release_test_case = release_test_case_result.scalar_one_or_none()
    if release_test_case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test case is not assigned to release",
        )

    test_case = release_test_case.test_case
    result_entry = await db.execute(
        select(TestResult)
        .options(selectinload(TestResult.attachments))
        .where(
            TestResult.id_release == release_id,
            TestResult.id_test_case == test_case_id,
        )
    )
    test_result = result_entry.scalar_one_or_none()
    staged_deletions = await stage_result_attachment_deletions(
        [test_result] if test_result is not None else []
    )

    try:
        if test_result is not None:
            await db.delete(test_result)

        await db.delete(release_test_case)

        sibling_cases_result = await db.execute(
            select(ReleaseTestCase)
            .options(selectinload(ReleaseTestCase.test_case))
            .where(
                ReleaseTestCase.id_release == release_id,
                ReleaseTestCase.id_test_case != test_case_id,
            )
        )
        sibling_cases = sibling_cases_result.scalars().all()
        has_same_plan_case = any(
            sibling_case.test_case.id_test_plan == test_case.id_test_plan
            for sibling_case in sibling_cases
        )

        if not has_same_plan_case:
            release_test_plan_result = await db.execute(
                select(ReleaseTestPlan).where(
                    ReleaseTestPlan.id_release == release_id,
                    ReleaseTestPlan.id_test_plan == test_case.id_test_plan,
                )
            )
            release_test_plan = release_test_plan_result.scalar_one_or_none()
            if release_test_plan is not None:
                await db.delete(release_test_plan)

        await db.commit()
    except Exception:
        await db.rollback()
        await rollback_staged_object_deletions(staged_deletions)
        raise

    await commit_staged_object_deletions(staged_deletions)


async def remove_test_plan_from_release_scope(
    db: AsyncSession,
    current_user: User,
    release_id: int,
    test_plan_id: int,
    allowed_roles: set[str],
) -> None:
    await get_release_for_roles(db, current_user, release_id, allowed_roles)
    release_test_plan_result = await db.execute(
        select(ReleaseTestPlan).where(
            ReleaseTestPlan.id_release == release_id,
            ReleaseTestPlan.id_test_plan == test_plan_id,
        )
    )
    release_test_plan = release_test_plan_result.scalar_one_or_none()
    if release_test_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test plan is not assigned to release",
        )

    release_test_cases_result = await db.execute(
        select(ReleaseTestCase)
        .options(selectinload(ReleaseTestCase.test_case))
        .where(ReleaseTestCase.id_release == release_id)
    )
    release_test_cases = release_test_cases_result.scalars().all()
    result_entries: list[TestResult] = []
    cases_to_delete: list[ReleaseTestCase] = []

    for release_test_case in release_test_cases:
        if release_test_case.test_case.id_test_plan != test_plan_id:
            continue

        result_entry = await db.execute(
            select(TestResult)
            .options(selectinload(TestResult.attachments))
            .where(
                TestResult.id_release == release_id,
                TestResult.id_test_case == release_test_case.id_test_case,
            )
        )
        test_result = result_entry.scalar_one_or_none()
        if test_result is not None:
            result_entries.append(test_result)

        cases_to_delete.append(release_test_case)

    staged_deletions = await stage_result_attachment_deletions(result_entries)

    try:
        for test_result in result_entries:
            await db.delete(test_result)
        for release_test_case in cases_to_delete:
            await db.delete(release_test_case)
        await db.delete(release_test_plan)
        await db.commit()
    except Exception:
        await db.rollback()
        await rollback_staged_object_deletions(staged_deletions)
        raise

    await commit_staged_object_deletions(staged_deletions)
