from enum import StrEnum


class LogTag(StrEnum):
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"

    INFO = "INFO"
    DEBUG = "DEBUG"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    QUERY = "QUERY"
