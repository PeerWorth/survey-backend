from fastapi import Depends
from redis.asyncio import Redis

from app.common.repository.abstract_redis_repository import AbstractRedisRepository
from database.dependency import get_redis_pool


class SalarySubmissionRedisRepository(AbstractRedisRepository):
    def __init__(self, redis: Redis = Depends(get_redis_pool)):
        super().__init__(redis)

    async def get(self, key: str) -> str | None:
        return await self._redis.get(key)

    async def set(self, key: str, value: str, expire: int, nx: bool = False) -> str | None:
        return await self._redis.set(key, value, ex=expire, nx=nx)
