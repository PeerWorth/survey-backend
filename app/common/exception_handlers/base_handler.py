from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.common.middleware.logger import middleware_logger
from app.common.schemas.base_schema import ErrorDetail, ErrorResponse


async def validation_exception_handler(request: Request, exc: ValidationError):
    middleware_logger.error(f"ValidationError: {exc.errors()}")
    detail_dict = {".".join(str(loc) for loc in err["loc"]): err["msg"] for err in exc.errors()}
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="요청 유효성 검사에 실패했습니다.",
            error=ErrorDetail(
                type="ValidationError",
                details=detail_dict,
            ),
        ).model_dump(),
    )


async def integrity_exception_handler(request: Request, exc: IntegrityError):
    middleware_logger.error(f"IntegrityError: {exc.orig}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=ErrorResponse(
            code=status.HTTP_409_CONFLICT,
            message="이미 존재하는 데이터입니다.",
            error=ErrorDetail(
                type="IntegrityError",
                details={"db_error": str(exc.orig)},
            ),
        ).model_dump(),
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    middleware_logger.critical(f"Unhandled Exception: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="서버 내부 오류가 발생했습니다.",
            error=ErrorDetail(type="InternalServerError", details={"exception": str(exc)}),
        ).model_dump(),
    )


async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    middleware_logger.error(f"RequestValidationError: {exc.errors()}")
    detail_dict = {".".join(str(loc) for loc in err["loc"]): err["msg"] for err in exc.errors()}
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Request validation failed.",
            error=ErrorDetail(type="RequestValidationError", details=detail_dict),
        ).model_dump(),
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    middleware_logger.warning(f"HTTPException: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.status_code,
            message=exc.detail if isinstance(exc.detail, str) else "HTTP 예외가 발생했습니다.",
            error=ErrorDetail(
                type="HTTPException",
                details=exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail)},
            ),
        ).model_dump(),
    )
