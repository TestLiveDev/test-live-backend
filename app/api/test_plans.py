# ruff: noqa: B008

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import TestPlan
from app.schemas.test_plan import TestPlanCreate, TestPlanRead, TestPlanUpdate
from app.security import (
    DELETE_ROLES,
    READ_ROLES,
    WRITE_ROLES,
    get_current_user,
)
from app.services.resource_access import (
    get_project_for_roles,
    get_test_plan_for_roles,
)

router = APIRouter(prefix="/api/test-plans", tags=["test-plans"])


@router.get("", response_model=list[TestPlanRead])
async def get_test_plans(
    project_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = select(TestPlan).options(selectinload(TestPlan.project))
    if project_id is not None:
        await get_project_for_roles(db, current_user, project_id, READ_ROLES)
        query = query.where(TestPlan.id_project == project_id)
    if project_id is None:
        from app.models import ProjectMember

        query = query.join(
            ProjectMember, ProjectMember.id_project == TestPlan.id_project
        ).where(ProjectMember.id_user == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=TestPlanRead, status_code=status.HTTP_201_CREATED)
async def create_test_plan(
    test_plan_data: TestPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await get_project_for_roles(
        db,
        current_user,
        test_plan_data.id_project,
        WRITE_ROLES,
    )

    test_plan = TestPlan(**test_plan_data.model_dump())
    db.add(test_plan)
    await db.commit()
    await db.refresh(test_plan, ["project"])
    return test_plan


@router.patch("/{test_plan_id}", response_model=TestPlanRead)
async def update_test_plan(
    test_plan_id: int,
    test_plan_data: TestPlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    test_plan = await get_test_plan_for_roles(
        db,
        current_user,
        test_plan_id,
        WRITE_ROLES,
        selectinload(TestPlan.project),
    )

    if test_plan_data.name is not None:
        test_plan.name = test_plan_data.name
    if test_plan_data.description is not None:
        test_plan.description = test_plan_data.description

    await db.commit()
    await db.refresh(test_plan)
    return test_plan


@router.delete("/{test_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_plan(
    test_plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    test_plan = await get_test_plan_for_roles(
        db,
        current_user,
        test_plan_id,
        DELETE_ROLES,
    )

    await db.delete(test_plan)
    await db.commit()
