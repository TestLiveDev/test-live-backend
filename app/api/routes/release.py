from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from app.models import Release
from app.api.deps import get_db
from app.schemas import ReleaseDBQuery, ReleaseCreate, ReleaseUpdate, ReleaseDelete
from pydantic import StrictBool

router = APIRouter(prefix='/release', tags=['Release'])


@router.get('/{id_organization}', response_model=list[ReleaseDBQuery])
async def get_release(id_organization: int, db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(Release).where(Release.id_organization == id_organization))).scalars().all()


@router.post('')
async def add_release(item: ReleaseCreate, db: AsyncSession = Depends(get_db)) -> StrictBool:
    obj = Release(**dict(item))
    db.add(obj)
    await db.commit()
    return True


@router.put('')
async def upd_organization(item: ReleaseUpdate, db: AsyncSession = Depends(get_db)):
    values = dict(item)
    del values['id_release']

    await db.execute(update(Release).values(**values).where(Release.id_release == item.id_release))
    await db.commit()
    return True


@router.delete('')
async def del_organization(item: ReleaseDelete, db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Release).where(Release.id_release == item.id_release))
    await db.commit()
    return True
