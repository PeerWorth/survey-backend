from enum import StrEnum


class EnvironmentType(StrEnum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"
    TEST = "test"

    @property
    def log_level(self) -> str:
        return "INFO" if self == EnvironmentType.PROD else "DEBUG"
