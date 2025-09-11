from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI.unicode_string(), pool_pre_ping=True)
async_session = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
