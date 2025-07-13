from fastapi import Request
from fastapi.responses import JSONResponse

from app.common.schemas.base_schema import ErrorDetail, ErrorResponse
from app.module.auth.errors.user_error import AuthException
from app.module.auth.logger import auth_logger


async def auth_exception_handler(request: Request, exc: AuthException):
    auth_logger.error(f"{exc.__class__.__name__}: {exc.detail}", exc_info=exc)

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.status_code,
            message="Auth 도메인 관련 오류가 발생했습니다.",
            error=ErrorDetail(
                type=exc.__class__.__name__,
                details=exc.detail if isinstance(exc.detail, dict) else {"message": exc.detail},
            ),
        ).model_dump(),
    )
