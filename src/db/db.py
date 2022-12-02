import sys
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import app_settings

Base: Any = declarative_base()

database_dsn = app_settings.database_dsn
if "pytest" in sys.modules:
    database_dsn = app_settings.test_database

engine = create_async_engine(database_dsn, future=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator:
    async with async_session() as session:
        yield session
