from abc import ABC, abstractmethod
from typing import Any, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

T = TypeVar("T", bound=SQLModel)


class BaseFactory(ABC):
    """테스트 데이터 생성을 위한 추상 베이스 팩토리 클래스"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def _save_and_refresh(self, entity: T) -> T:
        """Protected: 엔티티를 데이터베이스에 저장하고 새로고침"""
        self._session.add(entity)
        await self._session.commit()
        await self._session.refresh(entity)
        return entity

    async def _save_all_and_refresh(self, entities: list[T]) -> list[T]:
        """Protected: 여러 엔티티를 데이터베이스에 저장하고 새로고침"""
        self._session.add_all(entities)
        await self._session.commit()
        for entity in entities:
            await self._session.refresh(entity)
        return entities

    @abstractmethod
    async def create(self, *args: Any, **kwargs: Any) -> Any:  # type: ignore
        """추상 메서드: 테스트 데이터를 생성하고 반환"""
        pass
