from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import StrictBool

from app.api.deps import get_db
from app.schemas import OrganizationCreate, OrganizationDBQuery
from app.models import Oraganization


router = APIRouter(prefix='/organization', tags=['Organization'])

@router.get('', response_model=list[OrganizationDBQuery])
async def get_organization(db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(Oraganization))).scalars().all()


@router.post('')
async def add_organization(item: OrganizationCreate, db: AsyncSession = Depends(get_db)) -> StrictBool:

    obj = Oraganization(**dict(item))
    db.add(obj)
    await db.commit()
    return True


@router.put('')
async def upd_organization(db: AsyncSession = Depends(get_db)):
    return "Update Organization"


@router.delete('')
async def del_organization(db: AsyncSession = Depends(get_db)):
    return "Remove Organization"
