from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.dependency import get_mysql_session_router

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    def __init__(self, session: AsyncSession = Depends(get_mysql_session_router)):
        self.session = session

    async def commit_and_optional_refresh(self, instance: T, refresh: bool = False) -> Optional[T]:
        try:
            await self.session.flush()  # DB에 먼저 반영
            await self.session.commit()
            if refresh:
                await self.session.refresh(instance)
            return instance
        except IntegrityError as e:
            await self.session.rollback()
            raise e

    @abstractmethod
    async def save(self, instance: T, refresh: bool = False) -> Optional[T]:
        """인스턴스 저장 후 커밋하고 리턴"""
        ...

    @abstractmethod
    async def get(self, id_: Any) -> Optional[T]:
        """단일 객체 조회 (id 기준)"""
        ...

    # 공통 조회 헬퍼: id 하나로 조회
    async def _get_by_id(self, model: type[T], id_: Any) -> Optional[T]:
        stmt = select(model).where(getattr(model, "id") == id_)  # type: ignore
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
