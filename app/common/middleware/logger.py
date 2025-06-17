import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.common.enums import EnvironmentType
from app.common.logger.config import create_logger
from app.common.logger.constant import SLOW_LATENCY_MS
from app.common.logger.enums import LogTag
from main_config import settings

env_enum: EnvironmentType = settings.environment
cloudwatch_group = f"olass-{env_enum.log_env}-middleware"

middleware_logger = create_logger(name=__name__, level=env_enum.log_level, cloudwatch_group=cloudwatch_group)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        start = time.time()

        middleware_logger.info(
            f"id={request_id} method={request.method} path={request.url.path}", extra={"tag": LogTag.REQUEST.value}
        )

        try:
            response = await call_next(request)
        except Exception as e:
            middleware_logger.error(f"id={request_id} path={request.url.path}", exc_info=e)
            raise

        latency = int((time.time() - start) * 1000)  # ms 계산을 위해 1000 곱함

        if latency > SLOW_LATENCY_MS:
            middleware_logger.warning(
                f"SLOWREQUEST: latency_ms={latency} method={request.method} path={request.url.path}"
            )

        middleware_logger.info(
            f"id={request_id} status={response.status_code} latency_ms={latency}", extra={"tag": LogTag.RESPONSE.value}
        )
        response.headers["X-Request-ID"] = request_id
        return response
