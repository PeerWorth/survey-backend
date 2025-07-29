from abc import ABC, abstractmethod
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
from app.common.middleware.query_monitoring_middleware import QueryMonitoringMiddleware
from app.common.response import CustomJSONResponse

load_dotenv()


class AppConfig(ABC):
    """환경별 애플리케이션 설정을 관리하는 추상 클래스"""

    @abstractmethod
    def setup_app(self) -> FastAPI:
        """FastAPI 애플리케이션 인스턴스를 생성합니다."""
        pass

    @abstractmethod
    def setup_middleware(self, app: FastAPI) -> None:
        """미들웨어를 설정합니다."""
        pass

    @abstractmethod
    def setup_router(self, app: FastAPI) -> None:
        """라우터를 설정합니다."""
        pass


class BaseAppConfig(AppConfig):
    """공통 애플리케이션 설정을 구현하는 베이스 클래스"""

    def create_app(self) -> FastAPI:
        """애플리케이션 전체 설정을 수행합니다."""
        app = self.setup_app()
        self.setup_middleware(app)
        self.setup_router(app)
        return app

    def setup_middleware(self, app: FastAPI) -> None:
        """공통 미들웨어를 설정합니다."""
        # CORS 설정
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self._cors_origins(),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 공통 미들웨어
        register_exception_handlers(app)
        setup_database_monitoring()
        app.add_middleware(LoggingMiddleware)

    def setup_router(self, app: FastAPI) -> None:
        """라우터를 설정합니다."""
        app.include_router(asset_router, prefix="/api/asset", tags=["asset"])
        app.include_router(auth_router, prefix="/api/user", tags=["user"])

        @app.get("/health")
        async def health():
            return {"status": "ok"}

    @abstractmethod
    def _cors_origins(self) -> list[str]:
        """CORS origins를 반환합니다."""
        pass


class ProductionAppConfig(BaseAppConfig):
    """Production 환경 설정"""

    def setup_app(self) -> FastAPI:
        return FastAPI(docs_url=None, redoc_url=None, openapi_url=None, default_response_class=CustomJSONResponse)

    def _cors_origins(self) -> list[str]:
        return ["https://www.olass.co.kr"]


class DevelopmentAppConfig(BaseAppConfig):
    """Development 환경 설정"""

    def setup_app(self) -> FastAPI:
        return FastAPI(default_response_class=CustomJSONResponse)

    def _cors_origins(self) -> list[str]:
        return ["*"]

    def setup_middleware(self, app: FastAPI) -> None:
        """Development 환경 전용 미들웨어 설정"""
        super().setup_middleware(app)
        app.add_middleware(QueryMonitoringMiddleware, enable_detailed_logging=True)

    def setup_router(self, app: FastAPI) -> None:
        """Development 환경 전용 라우터 설정 (debug 라우터 포함)"""
        super().setup_router(app)
        app.include_router(debug_router, prefix="/api/asset", tags=["debug"])


class AppFactory:
    """환경에 따른 적절한 AppConfig 인스턴스를 생성하는 팩토리 클래스"""

    @staticmethod
    def create_factory() -> BaseAppConfig:
        """환경 값에 따라 적절한 AppConfig 인스턴스를 반환합니다."""
        ENVIRONMENT = getenv("ENVIRONMENT", None)
        if ENVIRONMENT == EnvironmentType.PROD.value:
            return ProductionAppConfig()
        else:
            return DevelopmentAppConfig()
