from os import getenv

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.asset.v1.router import asset_router
from app.api.auth.v1.router import auth_router
from app.common.enums import EnvironmentType
from app.common.exception_handlers.handler_register import register_exception_handlers
from app.common.middleware.logger import LoggingMiddleware

load_dotenv()

ENVIRONMENT = getenv("ENVIRONMENT", None)


if ENVIRONMENT == EnvironmentType.PROD.value:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://www.olass.co.kr"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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

register_exception_handlers(app)


app.add_middleware(LoggingMiddleware)


app.include_router(asset_router, prefix="/api/asset", tags=["asset"])
app.include_router(auth_router, prefix="/api/user", tags=["user"])


@app.get("/health")
async def health():
    return {"status": "ok"}
