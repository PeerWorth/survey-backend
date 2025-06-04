import asyncio
from os import getenv

import pytest
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlmodel import SQLModel

from database.dependency import get_mysql_session_router
from main import app

load_dotenv()

TEST_DATABASE_URL = getenv("TEST_DATABASE_URL", None)
test_engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True, poolclass=AsyncAdaptedQueuePool)
TestSessionLocal = sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def session():
    async def create_tables():
        async with test_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def drop_tables():
        async with test_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)

    await create_tables()

    async with TestSessionLocal() as test_session:
        yield test_session
        await test_session.rollback()

    await drop_tables()


def override_get_mysql_session_router():
    async def _override():
        async with TestSessionLocal() as session:
            yield session

    return _override


app.dependency_overrides[get_mysql_session_router] = override_get_mysql_session_router()
