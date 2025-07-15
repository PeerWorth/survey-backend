from typing import Awaitable, Callable

from enums import EmailType

EmailTargetHandler = Callable[[], Awaitable[list[list[tuple[int, str]]]]]

_registry: dict[EmailType, EmailTargetHandler] = {}


def register_email_target(email_type: EmailType):
    def wapper(fn: EmailTargetHandler):
        _registry[email_type] = fn
        return fn

    return wapper


def get_email_target_handler(email_type: EmailType) -> EmailTargetHandler:
    if email_type not in _registry:
        raise ValueError(f"핸들러가 등록되지 않은 email_type입니다: {email_type}")
    return _registry[email_type]
