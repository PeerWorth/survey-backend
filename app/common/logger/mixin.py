from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.common.logger.constant import EXCLUDE_PATHS


class ExcludePathsMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXCLUDE_PATHS:
            return await call_next(request)
        return await self.custom_dispatch(request, call_next)

    async def custom_dispatch(self, request: Request, call_next):
        raise NotImplementedError("커스텀 dispatch를 정의해주세요")
