class SalaryRecordNotFoundError(Exception):
    """Client에서 전달한 UUID에 해당하는 salary 레코드를 찾을 수 없음"""


class SalaryAlreadyLinkedError(Exception):
    """해당 salary 레코드가 이미 User와 연결되어 있음"""


class UserCreationFailedError(Exception):
    """User 저장에 실패함"""


class ConsentCreationFailedError(Exception):
    """UserConsent 저장에 실패함"""
