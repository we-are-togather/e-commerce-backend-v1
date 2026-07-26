from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# engine = create_engine(settings.database_url, future=True)
# SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

engine = create_async_engine(settings.database_url)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)