from enum import StrEnum
from os import getenv

from app.common.logger.enums import LogTag


class EnvironmentType(StrEnum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"
    TEST = "test"

    @property
    def log_level(self) -> str:
        return LogTag.INFO.value if self == EnvironmentType.PROD else LogTag.DEBUG.value

    @property
    def log_env(self) -> str:
        return "dev" if self in (EnvironmentType.LOCAL, EnvironmentType.TEST) else self.value


class DB_URL(StrEnum):
    LOCAL = "LOCAL_MYSQL_URL"
    TEST = "LOCAL_MYSQL_URL"
    DEV = "DEV_MYSQL_URL"
    PROD = "PROD_MYSQL_URL"

    @classmethod
    def from_env(cls, env: EnvironmentType) -> str:
        key = cls[env.name].value
        url = getenv(key)
        if not url:
            raise ValueError(f"{key} 환경변수가 설정되지 않았습니다.")
        return url


class REDIS_URL(StrEnum):
    LOCAL = "LOCAL_REDIS_HOST"
    TEST = "LOCAL_REDIS_HOST"
    DEV = "DEV_REDIS_HOST"
    PROD = "PROD_REDIS_HOST"

    @classmethod
    def from_env(cls, env: EnvironmentType) -> str:
        key = cls[env.name].value
        url = getenv(key)
        if not url:
            raise ValueError(f"{key} 환경변수가 설정되지 않았습니다.")
        return url
