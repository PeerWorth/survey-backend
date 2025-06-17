import json
from typing import Any, Generic, TypeVar

from app.common.redis_repository.abstract_redis_repository import AbstractRedisRepository

T = TypeVar("T")


class GeneralRedisRepository(AbstractRedisRepository, Generic[T]):
    async def get(self, key: str) -> T | None:
        value = await self.redis.get(key)
        if value is None:
            return None
        return self._deserialize(value)

    async def set(self, key: str, value: T, expire: int, nx: bool | None = None) -> bool | None:
        return await self.redis.set(key, self._serialize(value), ex=expire, nx=nx)  # type: ignore

    def _serialize(self, value: T) -> str:
        return str(value)

    def _deserialize(self, value: str) -> T:
        return value  # type: ignore


class IntRedisRepository(GeneralRedisRepository[int]):
    def _deserialize(self, value: str) -> int:
        return int(value)


class JsonRedisRepository(GeneralRedisRepository[dict[str, Any]]):
    def _serialize(self, value: dict[str, Any]) -> str:
        return json.dumps(value)

    def _deserialize(self, value: str) -> dict[str, Any]:
        return json.loads(value)


class ListRedisRepository(GeneralRedisRepository[list[T]]):
    def _serialize(self, value: list[T]) -> str:
        return json.dumps(value, default=str)

    def _deserialize(self, value: str) -> list[T]:
        return json.loads(value)
