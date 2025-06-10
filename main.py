from os import getenv

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api.asset.v1.router import asset_router
from app.api.auth.v1.router import auth_router
from app.common.enums import EnvironmentType
from app.common.middleware.logger import LoggingMiddleware, middleware_logger
from app.module.asset.errors.asset_error import AssetException
from app.module.asset.logger import asset_logger
from app.module.auth.errors.user_error import AuthException
from app.module.auth.logger import auth_logger

load_dotenv()

ENVIRONMENT = getenv("ENVIRONMENT", None)


if ENVIRONMENT == EnvironmentType.PROD.value:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://www.olass.co.kr"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

else:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# INFO: 도메인 별, 에러 핸들링 적용
@app.exception_handler(AssetException)
async def asset_exception_handler(request: Request, exc: AssetException):
    asset_logger.error(f"{exc.__class__.__name__}: {exc.detail}", exc_info=exc)
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException):
    auth_logger.error(f"{exc.__class__.__name__}: {exc.detail}", exc_info=exc)
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    middleware_logger.error(f"ValidationError: {exc.errors()}")
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=exc.errors())


app.add_middleware(LoggingMiddleware)


app.include_router(asset_router, prefix="/api/asset", tags=["asset"])
app.include_router(auth_router, prefix="/api/user", tags=["user"])


@app.get("/health")
async def health():
    return {"status": "ok"}
