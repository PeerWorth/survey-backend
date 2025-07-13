from http import HTTPStatus
from typing import Any, Dict

from app.common.schemas.base_schema import ErrorResponse

COMMON_ERROR_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    HTTPStatus.UNPROCESSABLE_ENTITY.value: {
        "model": ErrorResponse,
        "description": "요청 유효성 검사에 실패했습니다. (ValidationError, RequestValidationError)",
        "content": {
            "application/json": {
                "example": {
                    "code": 422,
                    "message": "요청 유효성 검사에 실패했습니다.",
                    "error": {"type": "ValidationError", "details": {"email": "이메일 형식이 잘못되었습니다."}},
                    "success": False,
                }
            }
        },
    },
    HTTPStatus.CONFLICT.value: {
        "model": ErrorResponse,
        "description": "이미 존재하는 데이터입니다. (IntegrityError)",
        "content": {
            "application/json": {
                "example": {
                    "code": 409,
                    "message": "이미 존재하는 데이터입니다.",
                    "error": {
                        "type": "IntegrityError",
                        "details": {"db_error": "Duplicate entry 'user@example.com' for key 'email_UNIQUE'"},
                    },
                    "success": False,
                }
            }
        },
    },
    HTTPStatus.INTERNAL_SERVER_ERROR.value: {
        "model": ErrorResponse,
        "description": "서버 내부 오류가 발생했습니다. (Unhandled Exception)",
        "content": {
            "application/json": {
                "example": {
                    "code": 500,
                    "message": "서버 내부 오류가 발생했습니다.",
                    "error": {
                        "type": "InternalServerError",
                        "details": {"exception": "Unexpected error occurred in processing request"},
                    },
                    "success": False,
                }
            }
        },
    },
    HTTPStatus.BAD_REQUEST.value: {
        "model": ErrorResponse,
        "description": "잘못된 요청입니다. (HTTPException 400 등)",
        "content": {
            "application/json": {
                "example": {
                    "code": 400,
                    "message": "잘못된 요청입니다.",
                    "error": {"type": "HTTPException", "details": {"message": "Invalid query parameter: page"}},
                    "success": False,
                }
            }
        },
    },
}
