from fastapi import Depends, Header, HTTPException, Request, status
from redis.asyncio import Redis

from app.api.asset.v1.constant import REDIS_KEY_RATE_LIMIT_SALARY_SUBMIT
from app.module.asset.redis_repository import SalarySubmissionRedisRepository


class SalarySubmissionRateLimiter:
    def __init__(
        self,
        redis_repo: Redis = Depends(SalarySubmissionRedisRepository),
        max_calls: int = 1,
        period: int = 60,
    ):
        self.redis_repo = redis_repo
        self.max_calls = max_calls
        self.period = period

    async def enforce_rate_limit(
        self,
        request: Request,
        x_forwarded_for: str | None = Header(None, convert_underscores=False),
    ) -> None:
        client_ip = self._parse_client_ip(request, x_forwarded_for)

        if not client_ip:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="클라이언트 IP를 확인할 수 없습니다.",
            )

        key = f"{REDIS_KEY_RATE_LIMIT_SALARY_SUBMIT}:{client_ip}"

        was_set = await self.redis_repo.set(key, 1, expire=self.period, nx=True)

        if not was_set:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="잠시 후 다시 시도해 주세요.")

    def _parse_client_ip(
        self,
        request: Request,
        x_forwarded_for: str | None,
    ) -> str | None:
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.client.host


async def salary_rate_limit_guard(
    request: Request,
    limiter: SalarySubmissionRateLimiter = Depends(SalarySubmissionRateLimiter),
    x_forwarded_for: str | None = Header(None, convert_underscores=False),
) -> None:
    await limiter.enforce_rate_limit(request, x_forwarded_for)
