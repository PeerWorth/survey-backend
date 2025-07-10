from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.common.exception_handlers.asset_handler import asset_exception_handler
from app.common.exception_handlers.auth_handler import auth_exception_handler
from app.common.exception_handlers.base_handler import (
    http_exception_handler,
    integrity_exception_handler,
    request_validation_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.module.asset.errors.asset_error import AssetException
from app.module.auth.errors.user_error import AuthException


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)  # type: ignore[HandlerTypeIssue]
    app.add_exception_handler(AuthException, auth_exception_handler)  # type: ignore[HandlerTypeIssue]
    app.add_exception_handler(AssetException, asset_exception_handler)  # type: ignore[HandlerTypeIssue]
    app.add_exception_handler(ValidationError, validation_exception_handler)  # type: ignore[HandlerTypeIssue]
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[HandlerTypeIssue]
    app.add_exception_handler(IntegrityError, integrity_exception_handler)  # type: ignore[HandlerTypeIssue]
    app.add_exception_handler(Exception, unhandled_exception_handler)  # type: ignore[HandlerTypeIssue]
