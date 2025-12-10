from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas import TestCaseCreate, TestCaseDelete
from app.crud import crud_test_case
from app.models import TestCase


router = APIRouter(prefix='/test_case', tags=['Test Case'])


@router.post('')
async def add_test_case(item: TestCaseCreate, db: AsyncSession = Depends(get_db)):
    await crud_test_case.create(db, dict(item))
    await db.commit()
    return True


@router.delete('')
async def del_organization(item: TestCaseDelete, db: AsyncSession = Depends(get_db)):
    await crud_test_case.delete(db, TestCase.id_test_case == item.id_test_case)
    await db.commit()
    return True
