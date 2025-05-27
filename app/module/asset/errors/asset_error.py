from starlette import status


class AssetException(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "서버 오류"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.detail


class SalaryStatNotFound(AssetException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "주어진 job_id와 experience에 대응하는 SalaryStat이 없습니다."


class NoMatchUserSalary(AssetException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "uuid와 매칭되는 UserSalary 정보를 못 찾았습니다."
