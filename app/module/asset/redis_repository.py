from app.common.repository.abstract_redis_repository import AbstractRedisRepository


class SalarySubmissionRedisRepository(AbstractRedisRepository):
    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)

    async def set(self, key: str, value: int, expire: int, nx: bool | None) -> str | None:
        return await self.redis.set(key, value, ex=expire, nx=nx)
