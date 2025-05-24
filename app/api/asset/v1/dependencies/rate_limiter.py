from fastapi import Depends, Header, HTTPException, Request, status

from app.api.asset.v1.constant import REDIS_KEY_RATE_LIMIT_SALARY_SUBMIT
from app.module.asset.logger import asset_logger
from app.module.asset.redis_repository import SalarySubmissionRedisRepository
from main_config import settings


class SalarySubmissionRateLimiter:
    def __init__(
        self,
        redis_repo: SalarySubmissionRedisRepository = Depends(SalarySubmissionRedisRepository),
        max_calls: int = settings.rate_limit_max_calls,
        period: int = settings.rate_limit_period,
    ):
        self.redis_repo = redis_repo
        self.max_calls = max_calls
        self.period = period

    async def enforce_rate_limit(
        self,
        request: Request,
        x_forwarded_for: str | None = Header(None, alias="X-Forwarded-For"),
        x_real_ip: str | None = Header(None, alias="X-Real-IP"),
    ) -> None:
        client_ip = self._parse_client_ip(request, x_forwarded_for, x_real_ip)

        if not client_ip:
            asset_logger.error(
                "[SalaryRateLimiter][ClientIPParseFailed] " "클라이언트 IP를 추출하지 못했습니다. " "request_url=%s",
                request.url.path,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="클라이언트 IP를 확인할 수 없습니다.",
            )

        key = f"{REDIS_KEY_RATE_LIMIT_SALARY_SUBMIT}:{client_ip}"

        was_set = await self.redis_repo.set(key=key, value=1, expire=self.period, nx=True)

        if not was_set:
            asset_logger.error(
                "[SalaryRateLimiter][RateLimitExceeded] " "Rate limit 초과: client_ip=%s, max_calls=%d, period=%ds",
                client_ip,
                self.max_calls,
                self.period,
            )
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="잠시 후 다시 시도해 주세요.")

    def _parse_client_ip(self, request: Request, x_forwarded_for: str | None, x_real_ip: str | None) -> str | None:
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        elif x_real_ip:
            return x_real_ip
        else:
            return request.client.host


async def salary_rate_limit_guard(
    request: Request,
    limiter: SalarySubmissionRateLimiter = Depends(),
    x_forwarded_for: str | None = Header(None, alias="X-Forwarded-For"),
    x_real_ip: str | None = Header(None, alias="X-Real-IP"),
) -> None:
    await limiter.enforce_rate_limit(request, x_forwarded_for, x_real_ip)
