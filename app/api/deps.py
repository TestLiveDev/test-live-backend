from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from app.manager.pg_session import async_session


async def get_db():
    async with async_session() as session:
        yield session
