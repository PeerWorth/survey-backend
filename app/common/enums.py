from enum import StrEnum

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
