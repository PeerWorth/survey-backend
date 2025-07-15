from os import getenv
from typing import AsyncGenerator

from dotenv import load_dotenv
from redis.asyncio import ConnectionPool, Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import REDIS_URL, EnvironmentType
from database.config import mysql_session_factory
from database.constant import DB_POOL_SIZE, REDIS_SOCKET_CONNECTION_TIMEOUT_SECOND

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


async def get_mysql_session_router() -> AsyncGenerator[AsyncSession, None]:
    session = mysql_session_factory()
    try:
        yield session
    finally:
        await session.close()


def get_redis_pool() -> Redis:
    pool = ConnectionPool(
        host=REDIS_HOST,
        port=REDIS_PORT,
        max_connections=DB_POOL_SIZE,
        decode_responses=True,
        socket_connect_timeout=REDIS_SOCKET_CONNECTION_TIMEOUT_SECOND,
        socket_timeout=REDIS_SOCKET_CONNECTION_TIMEOUT_SECOND,
    )
    return Redis(connection_pool=pool)
