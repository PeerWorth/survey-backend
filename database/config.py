import time
from os import getenv
from typing import Any, Mapping, Sequence

from dotenv import load_dotenv
from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.common.enums import EnvironmentType
from app.common.logger.enums import LogTag
from database.constant import (
    CONNECTION_TIMEOUT_SECOND,
    DEV_COLLECT_MAX_OVERFLOW,
    DEV_COLLECT_POOL_SIZE,
    DEV_MAX_OVERFLOW,
    DEV_POOL_SIZE,
    POOL_TIMEOUT_SECOND,
    PROD_COLLECT_MAX_OVERFLOW,
    PROD_COLLECT_POOL_SIZE,
    PROD_MAX_OVERFLOW,
    PROD_POOL_SIZE,
)
from database.logger import db_logger

load_dotenv()


ENVIRONMENT = getenv("ENVIRONMENT", None)
QUERY_LOG = getenv("QUERY_LOG", False)


if ENVIRONMENT == EnvironmentType.LOCAL.value or ENVIRONMENT == EnvironmentType.TEST.value:
    MYSQL_URL = getenv("LOCAL_MYSQL_URL", None)
    if not MYSQL_URL:
        raise ValueError()
    mysql_engine = create_async_engine(
        url=MYSQL_URL, pool_pre_ping=True, echo=False, pool_size=DEV_POOL_SIZE, max_overflow=DEV_MAX_OVERFLOW
    )
    collection_mysql_engine = create_async_engine(
        MYSQL_URL,
        pool_pre_ping=True,
        pool_size=DEV_COLLECT_POOL_SIZE,
        max_overflow=DEV_COLLECT_MAX_OVERFLOW,
        pool_timeout=POOL_TIMEOUT_SECOND,
        connect_args={"connect_timeout": CONNECTION_TIMEOUT_SECOND},
    )


elif ENVIRONMENT == EnvironmentType.DEV.value:
    MYSQL_URL = getenv("DEV_MYSQL_URL", None)
    if not MYSQL_URL:
        raise ValueError()
    mysql_engine = create_async_engine(
        url=MYSQL_URL, pool_pre_ping=True, echo=False, pool_size=DEV_POOL_SIZE, max_overflow=DEV_MAX_OVERFLOW
    )
    collection_mysql_engine = create_async_engine(
        MYSQL_URL,
        pool_pre_ping=True,
        pool_size=DEV_COLLECT_POOL_SIZE,
        max_overflow=DEV_COLLECT_MAX_OVERFLOW,
        pool_timeout=POOL_TIMEOUT_SECOND,
        connect_args={"connect_timeout": CONNECTION_TIMEOUT_SECOND},
    )
elif ENVIRONMENT == EnvironmentType.PROD.value:
    MYSQL_URL = getenv("PROD_MYSQL_URL", None)
    if not MYSQL_URL:
        raise ValueError()
    mysql_engine = create_async_engine(
        MYSQL_URL,
        pool_pre_ping=True,
        pool_size=PROD_POOL_SIZE,
        max_overflow=PROD_MAX_OVERFLOW,
        pool_timeout=POOL_TIMEOUT_SECOND,
        connect_args={"connect_timeout": CONNECTION_TIMEOUT_SECOND},
    )

    collection_mysql_engine = create_async_engine(
        MYSQL_URL,
        pool_pre_ping=True,
        pool_size=PROD_COLLECT_POOL_SIZE,
        max_overflow=PROD_COLLECT_MAX_OVERFLOW,
        pool_timeout=POOL_TIMEOUT_SECOND,
        connect_args={"connect_timeout": CONNECTION_TIMEOUT_SECOND},
    )
else:
    raise ValueError(f"{ENVIRONMENT} 환경변수 설정이 잘못되었습니다.")


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
collection_mysql_session_factory = sessionmaker(
    bind=collection_mysql_engine, class_=AsyncSession, expire_on_commit=False
)
