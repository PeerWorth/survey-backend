from enum import StrEnum
from os import getenv


class EnvironmentType(StrEnum):
    DEV = "dev"
    PROD = "prod"

    @property
    def db_url(self) -> str:
        """환경별 데이터베이스 URL"""
        env_keys = {
            EnvironmentType.DEV: "DEV_MYSQL_URL",
            EnvironmentType.PROD: "PROD_MYSQL_URL",
        }
        key = env_keys[self]
        url = getenv(key)
        if not url:
            raise ValueError(f"{key} 환경변수가 설정되지 않았습니다.")
        return url

    @property
    def redis_host(self) -> str:
        """환경별 Redis 호스트"""
        env_keys = {
            EnvironmentType.DEV: "DEV_REDIS_HOST",
            EnvironmentType.PROD: "PROD_REDIS_HOST",
        }
        key = env_keys[self]
        host = getenv(key)
        if not host:
            raise ValueError(f"{key} 환경변수가 설정되지 않았습니다.")
        return host

    @property
    def bigquery_host_jsons(self) -> str:
        """환경별 Bigquery 호스트"""
        env_keys = {
            EnvironmentType.DEV: "DEV_REDIS_HOST",
            EnvironmentType.PROD: "PROD_REDIS_HOST",
        }
        key = env_keys[self]
        host = getenv(key)
        if not host:
            raise ValueError(f"{key} 환경변수가 설정되지 않았습니다.")
        return host
