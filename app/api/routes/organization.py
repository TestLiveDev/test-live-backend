from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from pydantic import StrictBool

from app.api.deps import get_db
from app.schemas import OrganizationCreate, OrganizationUpdate, OrganizationDelete, OrganizationDBQuery
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
async def upd_organization(item: OrganizationUpdate, db: AsyncSession = Depends(get_db)):
    values = dict(item)
    del values['id_organization']
    await db.execute(update(Oraganization).values(**values).where(Oraganization.id_organization == item.id_organization))
    await db.commit()
    return True


@router.delete('')
async def del_organization(item: OrganizationDelete, db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Oraganization).where(Oraganization.id_organization == item.id_organization))
    await db.commit()
    return True
