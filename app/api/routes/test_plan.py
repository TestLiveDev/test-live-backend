from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.api.deps import get_db
from app.models import TestPlan
from app.schemas import TestPlanDBQuery, TestPlanCreate, TestPlanUpdate, TestPlanDelete

router = APIRouter(prefix='/test_plan', tags=['Test Plan'])

@router.get('/{id_organization}', response_model=list[TestPlanDBQuery])
async def get_test_plan(id_organization: int, db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(TestPlan).where(TestPlan.id_organization == id_organization))).scalars().all()


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
