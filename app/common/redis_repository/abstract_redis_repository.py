from abc import ABC, abstractmethod
from typing import Any

from fastapi import Depends
from redis.asyncio import Redis

from database.dependency import get_redis_pool


class AbstractRedisRepository(ABC):
    """
    Redis 필수 매소드 추상화
    """

    def __init__(self, redis: Redis = Depends(get_redis_pool)) -> None:
        self.redis = redis

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """
        단일 값 반환
        """

    @abstractmethod
    async def set(self, key: str, value: Any, expire: int, nx: bool | None) -> Any | None:
        """
        단일 값 추가/수정
        """
