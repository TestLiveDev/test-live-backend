from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, literal

from app.api.deps import get_db
from app.models import TestPlan, TestCase
from app.schemas import TestPlanDBQuery, TestPlanCreate, TestPlanUpdate, TestPlanDelete

router = APIRouter(prefix='/test_plan', tags=['Test Plan'])

@router.get('/{id_organization}', response_model=list[TestPlanDBQuery])
async def get_test_plan(id_organization: int, db: AsyncSession = Depends(get_db)):
    parent_test_plan = (
        select(TestPlan.id_test_plan,
               TestPlan.id_organization,
               TestPlan.id_parent,
               TestPlan.name_test_plan,
               TestCase.id_test_case,
               TestCase.name_test_case,
               literal(0).label('lvl'))
        .select_from(TestPlan)
        .outerjoin(TestCase, TestCase.id_test_plan == TestPlan.id_test_plan)
        .where(TestPlan.id_organization == id_organization,
               TestPlan.id_parent.is_(None))
    ).cte(name='main_testplans',recursive=True)
    childs_cte = parent_test_plan.union_all(
        select(TestPlan.id_test_plan,
               TestPlan.id_organization,
               TestPlan.id_parent,
               TestPlan.name_test_plan,
               TestCase.id_test_case,
               TestCase.name_test_case,
               (parent_test_plan.c.lvl + 1).label('lvl'))
        .select_from(TestPlan)
        .outerjoin(TestCase, TestCase.id_test_plan == TestPlan.id_test_plan)
        .join(parent_test_plan, parent_test_plan.c.id_test_plan == TestPlan.id_parent)
    )
    return (await db.execute(select(childs_cte).order_by(childs_cte.c.lvl.desc()))).fetchall()


@router.post('')
async def add_test_plan(item: TestPlanCreate, db: AsyncSession = Depends(get_db)):
    obj = TestPlan(**dict(item))
    db.add(obj)
    await db.commit()
    return True



@router.put('')
async def upd_organization(item: TestPlanUpdate, db: AsyncSession = Depends(get_db)):
    values = dict(item)
    del values['id_test_plan']

    await db.execute(
        update(TestPlan)
        .values(**values)
        .where(TestPlan.id_test_plan == item.id_test_plan)
    )
    await db.commit()
    return True


@router.delete('')
async def del_organization(item: TestPlanDelete, db: AsyncSession = Depends(get_db)):
    await db.execute(delete(TestPlan).where(TestPlan.id_test_plan == item.id_test_plan))
    await db.commit()
    return True
