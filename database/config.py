import time
from os import getenv
from typing import Any, Mapping, Sequence

from dotenv import load_dotenv
from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.common.enums import DB_URL, EnvironmentType
from app.common.logger.enums import LogTag
from database.constant import CONNECTION_TIMEOUT_SECOND, DB_MAX_OVERFLOW, DB_POOL_SIZE, POOL_TIMEOUT_SECOND
from database.logger import db_logger

load_dotenv()


ENVIRONMENT = getenv("ENVIRONMENT", None)
if not ENVIRONMENT:
    raise ValueError("ENVIRONMENT 환경변수가 설정되지 않았습니다.")

QUERY_LOG = getenv("QUERY_LOG", False)


try:
    env = EnvironmentType(ENVIRONMENT)  # type: ignore[arg-type]
except ValueError:
    raise ValueError(f"정의되지 않는 환경 변수 값입니다. {ENVIRONMENT=}")

MYSQL_URL = DB_URL.from_env(env)

mysql_engine = create_async_engine(
    MYSQL_URL,
    pool_pre_ping=True,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT_SECOND,
    connect_args={"connect_timeout": CONNECTION_TIMEOUT_SECOND},
)


@event.listens_for(mysql_engine.sync_engine, "before_cursor_execute")
def _before_cursor_execute(
    conn: Connection,
    cursor: Any,
    statement: str,
    parameters: Sequence[Any] | Mapping[str, Any],
    context: Any,
    executemany: bool,
) -> None:
    context._query_start_time = time.time()


@event.listens_for(mysql_engine.sync_engine, "after_cursor_execute")
def _after_cursor_execute(
    conn: Connection,
    cursor: Any,
    statement: str,
    parameters: Sequence[Any] | Mapping[str, Any],
    context: Any,
    executemany: bool,
) -> None:
    total_ms = (time.time() - context._query_start_time) * 1000

    try:
        if isinstance(parameters, dict):
            formatted_query = statement % {k: repr(v) for k, v in parameters.items()}
        else:
            formatted_query = statement % tuple(repr(v) for v in parameters)
    except Exception:
        formatted_query = f"{statement} -- {parameters}"

    if total_ms > 200:
        db_logger.warning(f"[SLOWQUERY] {total_ms=:.2f}ms\n{formatted_query}")
    else:
        db_logger.debug(f"{total_ms=:.2f}ms\n{formatted_query}", extra={"tag": LogTag.QUERY.value})


mysql_session_factory = sessionmaker(bind=mysql_engine, class_=AsyncSession, expire_on_commit=False)
