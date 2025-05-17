from starlette import status


class AuthException(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail: str = "서버 오류"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.default_detail


class SalaryNotFound(AuthException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "연봉 기록을 찾을 수 없습니다."


class SalaryAlreadyLinked(AuthException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "이미 연결된 연봉 기록입니다."


class UserCreationFailed(AuthException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "회원 생성에 실패했습니다."


class ConsentCreationFailed(AuthException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "동의 처리에 실패했습니다."
