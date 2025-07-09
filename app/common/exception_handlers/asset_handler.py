from fastapi import Request
from fastapi.responses import JSONResponse

from app.common.schemas.base_schema import ErrorDetail, ErrorResponse
from app.module.asset.errors.asset_error import AssetException
from app.module.asset.logger import asset_logger


async def asset_exception_handler(request: Request, exc: AssetException):
    asset_logger.error(f"{exc.__class__.__name__}: {exc.detail}", exc_info=exc)

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.status_code,
            message="Asset 도메인 관련 오류가 발생했습니다.",
            error=ErrorDetail(
                type=exc.__class__.__name__,
                details=exc.detail if isinstance(exc.detail, dict) else {"message": exc.detail},
            ),
        ).model_dump(),
    )
