import asyncio
from os import getenv
from test.fixtures.asset_fixture import job_factory  # noqa: F401
from test.fixtures.asset_fixture import job_group_factory  # noqa: F401
from test.fixtures.asset_fixture import salary_stat_factory  # noqa: F401
from test.fixtures.asset_fixture import user_profile_factory  # noqa: F401
from test.fixtures.asset_fixture import user_salary_factory  # noqa: F401
from test.fixtures.auth_fixture import user_consent_factory  # noqa: F401
from test.fixtures.auth_fixture import user_factory  # noqa: F401
from test.fixtures.full_fixture import full_test_data_builder  # noqa: F401

import pytest
from dotenv import load_dotenv
from httpx import AsyncClient
from redis.asyncio import ConnectionPool, Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlmodel import SQLModel

from app.common.enums import REDIS_URL, EnvironmentType
from app.common.redis_repository.general_redis_repository import (
    GeneralRedisRepository,
    IntRedisRepository,
    JsonRedisRepository,
)
from database.dependency import get_mysql_session_router
from main import app

load_dotenv()

ENVIRONMENT = getenv("ENVIRONMENT", None)
if not ENVIRONMENT:
    raise ValueError("ENVIRONMENT 환경변수가 설정되지 않았습니다.")
try:
    env = EnvironmentType(ENVIRONMENT)  # type: ignore[arg-type]
except ValueError:
    raise ValueError(f"정의되지 않는 환경 변수 값입니다. {ENVIRONMENT=}")


REDIS_HOST = REDIS_URL.from_env(env)
REDIS_PORT = int(getenv("REDIS_PORT", 6379))

TEST_DATABASE_URL = getenv("TEST_DATABASE_URL", None)


# 테스트용 엔진은 각 함수마다 새로 생성하도록 함수로 변경
def create_test_engine():
    return create_async_engine(
        TEST_DATABASE_URL,
        pool_pre_ping=True,
        poolclass=AsyncAdaptedQueuePool,
        pool_size=1,
        max_overflow=0,
        echo=False,
    )


# TestSessionLocal도 동적으로 생성하도록 변경


@pytest.fixture(scope="function")
async def redis_client():
    pool = ConnectionPool(
        host=getenv("TEST_REDIS_HOST", "localhost"),
        port=int(getenv("TEST_REDIS_PORT", 6379)),
        decode_responses=True,
        max_connections=10,
    )
    redis = Redis(connection_pool=pool)

    await redis.flushdb()

    yield redis

    await redis.flushdb()
    await redis.close()
    await pool.disconnect()


@pytest.fixture(scope="function")
def general_redis_repository(redis_client):
    repo = GeneralRedisRepository()
    repo.redis = redis_client
    return repo


@pytest.fixture(scope="function")
def int_redis_repository(redis_client):
    repo = IntRedisRepository()
    repo.redis = redis_client
    return repo


@pytest.fixture(scope="function")
def json_redis_repository(redis_client):
    repo = JsonRedisRepository()
    repo.redis = redis_client
    return repo


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def client(session):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def session():
    # 각 테스트마다 새 엔진 생성
    engine = create_test_engine()
    TestSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def drop_tables():
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)

    await create_tables()

    async with TestSessionLocal() as test_session:
        yield test_session
        await test_session.rollback()

    await drop_tables()
    await engine.dispose()


def override_get_mysql_session_router():
    async def _override():
        engine = create_test_engine()
        TestSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
        async with TestSessionLocal() as session:
            yield session
        await engine.dispose()

    return _override


def override_get_redis_pool(redis_client):
    def _override():
        return redis_client

    return _override


app.dependency_overrides[get_mysql_session_router] = override_get_mysql_session_router()
