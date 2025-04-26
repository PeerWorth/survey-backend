from abc import ABC, abstractmethod
from typing import Any

from redis.asyncio import Redis


class AbstractRedisRepository(ABC):
    """
    Redis 필수 매소드 추상화
    """

    def __init__(self, redis_client: Redis) -> None:
        self._redis = redis_client

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """
        단일 값 반환
        """

    @abstractmethod
    async def set(self, key: str, value: Any, expire: int) -> Any | None:
        """
        단일 값 추가/수정
        """
