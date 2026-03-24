# ruff: noqa: B008

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import TestCase
from app.schemas.test_case import TestCaseCreate, TestCaseRead, TestCaseUpdate
from app.security import (
    DELETE_ROLES,
    READ_ROLES,
    WRITE_ROLES,
    get_current_user,
)
from app.services.resource_access import (
    get_test_case_for_roles,
    get_test_plan_for_roles,
)
from app.services.status_service import (
    TEST_CASE_PRIORITY_CATEGORY,
    get_status_by_code_and_category,
    validate_status_category,
)

router = APIRouter(prefix="/api/test-cases", tags=["test-cases"])


@router.get("", response_model=list[TestCaseRead])
async def get_test_cases(
    test_plan_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = select(TestCase).options(
        selectinload(TestCase.priority), selectinload(TestCase.test_plan)
    )
    if test_plan_id:
        await get_test_plan_for_roles(
            db,
            current_user,
            test_plan_id,
            READ_ROLES,
        )
        query = query.where(TestCase.id_test_plan == test_plan_id)
    else:
        from app.models import ProjectMember, TestPlan

        query = (
            query.join(TestPlan)
            .join(ProjectMember, ProjectMember.id_project == TestPlan.id_project)
            .where(ProjectMember.id_user == current_user.id)
        )
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=TestCaseRead, status_code=status.HTTP_201_CREATED)
async def create_test_case(
    test_case_data: TestCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):

    await get_test_plan_for_roles(
        db,
        current_user,
        test_case_data.id_test_plan,
        WRITE_ROLES,
    )

    id_priority = test_case_data.id_priority
    if id_priority is None:
        priority = await get_status_by_code_and_category(
            db,
            "medium",
            TEST_CASE_PRIORITY_CATEGORY,
        )
        id_priority = priority.id
    else:
        await validate_status_category(
            db,
            id_priority,
            TEST_CASE_PRIORITY_CATEGORY,
        )

    test_case = TestCase(
        id_test_plan=test_case_data.id_test_plan,
        id_priority=id_priority,
        name=test_case_data.name,
        description=test_case_data.description,
        preconditions=test_case_data.preconditions,
        postconditions=test_case_data.postconditions,
    )
    db.add(test_case)
    await db.commit()
    await db.refresh(test_case, ["priority"])
    return test_case


@router.patch("/{test_case_id}", response_model=TestCaseRead)
async def update_test_case(
    test_case_id: int,
    test_case_data: TestCaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    test_case = await get_test_case_for_roles(
        db,
        current_user,
        test_case_id,
        WRITE_ROLES,
        selectinload(TestCase.priority),
        selectinload(TestCase.test_plan),
    )

    if test_case_data.name is not None:
        test_case.name = test_case_data.name
    if test_case_data.description is not None:
        test_case.description = test_case_data.description
    if test_case_data.preconditions is not None:
        test_case.preconditions = test_case_data.preconditions
    if test_case_data.postconditions is not None:
        test_case.postconditions = test_case_data.postconditions
    if test_case_data.id_priority is not None:
        await validate_status_category(
            db,
            test_case_data.id_priority,
            TEST_CASE_PRIORITY_CATEGORY,
        )
        test_case.id_priority = test_case_data.id_priority

    await db.commit()
    await db.refresh(test_case, ["priority"])
    return test_case


@router.delete("/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_case(
    test_case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    test_case = await get_test_case_for_roles(
        db,
        current_user,
        test_case_id,
        DELETE_ROLES,
        selectinload(TestCase.test_plan),
    )

    await db.delete(test_case)
    await db.commit()
