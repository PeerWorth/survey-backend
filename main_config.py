from pydantic_settings import BaseSettings, SettingsConfigDict

from app.common.enums import EnvironmentType


class Settings(BaseSettings):
    environment: EnvironmentType = EnvironmentType.LOCAL
    rate_limit_max_calls: int = 1
    rate_limit_period_sec_dev: int = 10
    rate_limit_period_sec_prod: int = 60 * 60 * 24

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        from_attributes=True,
        extra="ignore",
    )

    @property
    def rate_limit_period(self) -> int:
        env = self.environment.lower()
        if env in ("local", "dev"):
            return self.rate_limit_period_sec_dev
        else:
            return self.rate_limit_period_sec_prod


settings = Settings()
