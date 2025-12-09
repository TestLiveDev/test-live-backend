from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas import TestCaseCreate
from app.crud import crud_test_case


router = APIRouter(prefix='/test_case', tags=['Test Case'])


@router.post('')
async def add_test_case(item: TestCaseCreate, db: AsyncSession = Depends(get_db)):
    await crud_test_case.create(db, dict(item))
    await db.commit()
    return True
