import asyncio
from typing import AsyncGenerator, Generator

import asyncpg
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from db.db import Base, engine
from main import app


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='function')
async def client() -> AsyncGenerator:
    async with AsyncClient(
        app=app,
        base_url='http://127.0.0.1/api/v1'
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="module")
async def async_session() -> AsyncGenerator:
    async def connect_create_if_not_exists(user, database, password):
        try:
            conn = await asyncpg.connect(
                user=user,
                database=database,
                password=password,
                max_cached_statement_lifetime=6,
                host='127.0.0.1',
                port=5555
            )
        except asyncpg.InvalidCatalogNameError:
            sys_conn = await asyncpg.connect(
                database='postgres',
                user='postgres',
                password='postgres',
                host='127.0.0.1',
                port=5555
            )
#
            await sys_conn.execute(
                f'CREATE DATABASE "{database}" OWNER "{user}"'
            )
            await sys_conn.close()
            conn = await asyncpg.connect(
                user=user,
                database=database,
                password=password,
                host='127.0.0.1',
                port=5555
            )
            await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        return conn

    session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    await connect_create_if_not_exists(
        user='postgres',
        database='test_db',
        password='postgres')
    async with session() as s:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield s
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
