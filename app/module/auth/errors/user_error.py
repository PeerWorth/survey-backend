class SalaryRecordNotFound(Exception):
    """Client에서 전달한 UUID에 해당하는 salary 레코드를 찾을 수 없음"""


class SalaryAlreadyLinked(Exception):
    """해당 salary 레코드가 이미 User와 연결되어 있음"""


class UserCreationFailed(Exception):
    """User 저장에 실패함"""


class ConsentCreationFailed(Exception):
    """UserConsent 저장에 실패함"""
