from typing import Any, Dict

from starlette import status

from app.common.schemas.base_schema import ErrorResponse

AUTH_ERROR_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorResponse,
        "description": "이미 연결된 연봉 기록입니다.",
        "content": {
            "application/json": {
                "example": {
                    "code": 400,
                    "message": "User 도메인 관련 오류가 발생했습니다.",
                    "error": {"type": "SalaryAlreadyLinked", "details": {"message": "이미 연결된 연봉 기록입니다."}},
                    "success": False,
                }
            }
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "model": ErrorResponse,
        "description": "연봉 기록을 찾을 수 없습니다.",
        "content": {
            "application/json": {
                "example": {
                    "code": 404,
                    "message": "User 도메인 관련 오류가 발생했습니다.",
                    "error": {"type": "SalaryNotFound", "details": {"message": "연봉 기록을 찾을 수 없습니다."}},
                    "success": False,
                }
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "model": ErrorResponse,
        "description": "회원 생성 또는 동의 처리 실패",
        "content": {
            "application/json": {
                "examples": {
                    "UserCreationFailed": {
                        "summary": "회원 생성 실패",
                        "value": {
                            "code": 500,
                            "message": "User 도메인 관련 오류가 발생했습니다.",
                            "error": {
                                "type": "UserCreationFailed",
                                "details": {"message": "회원 생성에 실패했습니다."},
                            },
                            "success": False,
                        },
                    },
                    "ConsentCreationFailed": {
                        "summary": "동의 처리 실패",
                        "value": {
                            "code": 500,
                            "message": "User 도메인 관련 오류가 발생했습니다.",
                            "error": {
                                "type": "ConsentCreationFailed",
                                "details": {"message": "동의 처리에 실패했습니다."},
                            },
                            "success": False,
                        },
                    },
                }
            }
        },
    },
}
