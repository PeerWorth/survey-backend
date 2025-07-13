from os import getenv

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

MYSQL_URL = getenv("DEV_MYSQL_URL", None)

engine = create_async_engine(MYSQL_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    return SessionLocal()
