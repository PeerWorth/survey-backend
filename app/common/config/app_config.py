from abc import ABC, abstractmethod
from os import getenv

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.asset.v1.router import asset_router
from app.api.auth.v1.router import auth_router
from app.common.enums import EnvironmentType
from app.common.exception_handlers.handler_register import register_exception_handlers
from app.common.middleware.logger import LoggingMiddleware
from app.common.response import CustomJSONResponse

load_dotenv()


class AppConfig(ABC):
    @abstractmethod
    def setup_app(self) -> FastAPI:
        pass

    @abstractmethod
    def setup_middleware(self, app: FastAPI) -> None:
        pass

    @abstractmethod
    def setup_router(self, app: FastAPI) -> None:
        pass


class BaseAppConfig(AppConfig):
    def create_app(self) -> FastAPI:
        app = self.setup_app()
        self.setup_middleware(app)
        self.setup_router(app)
        return app

    def setup_middleware(self, app: FastAPI) -> None:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.cors_origins(),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app.add_middleware(LoggingMiddleware)
        register_exception_handlers(app)

    def setup_router(self, app: FastAPI) -> None:
        app.include_router(asset_router, prefix="/api/asset", tags=["asset"])
        app.include_router(auth_router, prefix="/api/user", tags=["user"])

        @app.get("/health")
        async def health():
            return {"status": "ok"}

    @abstractmethod
    def cors_origins(self) -> list[str]:
        pass


class ProductionAppConfig(BaseAppConfig):
    def setup_app(self) -> FastAPI:
        return FastAPI(docs_url=None, redoc_url=None, openapi_url=None, default_response_class=CustomJSONResponse)

    def cors_origins(self) -> list[str]:
        return ["https://www.olass.co.kr"]


class DevelopmentAppConfig(BaseAppConfig):
    def setup_app(self) -> FastAPI:
        return FastAPI(default_response_class=CustomJSONResponse)

    def cors_origins(self) -> list[str]:
        return ["*"]


class AppFactory:
    @staticmethod
    def create_factory() -> BaseAppConfig:
        ENVIRONMENT = getenv("ENVIRONMENT", None)
        if ENVIRONMENT == EnvironmentType.PROD.value:
            return ProductionAppConfig()
        else:
            return DevelopmentAppConfig()
