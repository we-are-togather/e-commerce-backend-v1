from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# engine = create_engine(settings.database_url, future=True)
# SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# print("========== DATABASE CONFIG ==========")
# print("HOST:", settings.postgres_host)
# print("PORT:", settings.postgres_port)
# print("USER:", settings.postgres_user)
# print("DB:", settings.postgres_db)

# print(
#     settings.database_url.replace(
#         settings.postgres_password,
#         "******"
#     )
# )
# print("=====================================")

engine = create_async_engine(settings.database_url)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)