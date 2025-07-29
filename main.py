from os import getenv

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.asset.v1.debug_router import debug_router
from app.api.asset.v1.router import asset_router
from app.api.auth.v1.router import auth_router
from app.common.database.monitoring_setup import setup_database_monitoring
from app.common.enums import EnvironmentType
from app.common.exception_handlers.handler_register import register_exception_handlers
from app.common.middleware.logger import LoggingMiddleware
from app.common.middleware.query_monitoring_middleware import setup_query_monitoring
from app.common.response import CustomJSONResponse

load_dotenv()

ENVIRONMENT = getenv("ENVIRONMENT", None)


if ENVIRONMENT == EnvironmentType.PROD.value:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, default_response_class=CustomJSONResponse)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://www.olass.co.kr"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app = FastAPI(default_response_class=CustomJSONResponse)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

register_exception_handlers(app)

# 데이터베이스 쿼리 모니터링 설정
setup_database_monitoring()

# 미들웨어 설정
app.add_middleware(LoggingMiddleware)

# 개발환경에서만 쿼리 모니터링 미들웨어 및 디버그 라우터 활성화
if ENVIRONMENT != EnvironmentType.PROD.value:
    setup_query_monitoring(app, enable_detailed_logging=True)
    app.include_router(debug_router, prefix="/api/asset", tags=["debug"])

app.include_router(asset_router, prefix="/api/asset", tags=["asset"])
app.include_router(auth_router, prefix="/api/user", tags=["user"])


@app.get("/health")
async def health():
    return {"status": "ok"}
