from sqlalchemy import Table, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

class CRUDBase:
    def __init__(self, model: Table, primary_key: str):
        self.model = model
        self.primary_key = primary_key
    
    async def get(self, db: AsyncSession, *args):
        res = await db.execute(select(self.model).where(*args).limit(1))
        return res.scalars().one_or_none()

    async def create(self, db: AsyncSession, values: dict):
        obj = self.model(**dict(values))
        db.add(obj)
        await db.flush()
        return obj

    async def update(self, db: AsyncSession, values: dict, *args):
        return await db.execute(
            update(self.model)
            .where(*args)
            .values(*values)
        )
    
    async def delete(self, db: AsyncSession, *args):
        return await db.execute(
            delete(self.model)
            .where(*args)
        )
