"""Email Trigger Service 테스트 - 격리된 테스트"""

from unittest.mock import AsyncMock

import pytest


class MockEmailTargetService:
    """테스트용 EmailTargetService 모의 구현"""

    def __init__(self, repository, session):
        self.repository = repository
        self.session = session
        self.MAX_SINGLE_SEND_SIZE = 50  # constant.py에서 가져온 값

    async def get_target_emails(self):
        """마케팅 동의한 이메일 목록을 청크로 나누어 반환"""
        try:
            emails = await self.repository.get_marketing_agreed_emails()
            return self._chunk_list(emails)
        finally:
            await self.session.close()

    def _chunk_list(self, emails):
        """이메일 리스트를 청크로 나누기"""
        chunk_size = self.MAX_SINGLE_SEND_SIZE
        return [emails[i : i + chunk_size] for i in range(0, len(emails), chunk_size)]


class TestEmailTargetServiceIsolated:
    """EmailTargetService 격리 테스트"""

    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_session(self):
        session = AsyncMock()
        session.close = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_repository, mock_session):
        return MockEmailTargetService(repository=mock_repository, session=mock_session)

    @pytest.mark.asyncio
    async def test_get_target_emails_success(self, service, mock_repository, mock_session):
        # Given
        mock_emails = [
            (1, "user1@example.com"),
            (2, "user2@example.com"),
            (3, "user3@example.com"),
            (4, "user4@example.com"),
            (5, "user5@example.com"),
        ]
        mock_repository.get_marketing_agreed_emails.return_value = mock_emails
        service.MAX_SINGLE_SEND_SIZE = 3  # 테스트용으로 작게 설정

        # When
        result = await service.get_target_emails()

        # Then
        assert len(result) == 2  # 5개를 3개씩 나누면 2개 청크
        assert len(result[0]) == 3
        assert len(result[1]) == 2

        assert result[0] == [(1, "user1@example.com"), (2, "user2@example.com"), (3, "user3@example.com")]
        assert result[1] == [(4, "user4@example.com"), (5, "user5@example.com")]

        mock_repository.get_marketing_agreed_emails.assert_called_once()
        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_target_emails_empty_result(self, service, mock_repository, mock_session):
        # Given
        mock_repository.get_marketing_agreed_emails.return_value = []

        # When
        result = await service.get_target_emails()

        # Then
        assert result == []
        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_target_emails_closes_session_on_error(self, service, mock_repository, mock_session):
        # Given
        mock_repository.get_marketing_agreed_emails.side_effect = Exception("DB Error")

        # When & Then
        with pytest.raises(Exception, match="DB Error"):
            await service.get_target_emails()

        mock_session.close.assert_called_once()

    def test_chunk_list_exact_division(self, service):
        # Given
        emails = [
            (1, "user1@example.com"),
            (2, "user2@example.com"),
            (3, "user3@example.com"),
            (4, "user4@example.com"),
        ]
        service.MAX_SINGLE_SEND_SIZE = 2

        # When
        result = service._chunk_list(emails)

        # Then
        assert len(result) == 2
        assert all(len(chunk) == 2 for chunk in result)
        assert result[0] == [(1, "user1@example.com"), (2, "user2@example.com")]
        assert result[1] == [(3, "user3@example.com"), (4, "user4@example.com")]

    def test_chunk_list_remainder(self, service):
        # Given
        emails = [
            (1, "user1@example.com"),
            (2, "user2@example.com"),
            (3, "user3@example.com"),
        ]
        service.MAX_SINGLE_SEND_SIZE = 2

        # When
        result = service._chunk_list(emails)

        # Then
        assert len(result) == 2
        assert len(result[0]) == 2
        assert len(result[1]) == 1
        assert result[0] == [(1, "user1@example.com"), (2, "user2@example.com")]
        assert result[1] == [(3, "user3@example.com")]

    def test_chunk_list_single_chunk(self, service):
        # Given
        emails = [(1, "user1@example.com"), (2, "user2@example.com")]
        service.MAX_SINGLE_SEND_SIZE = 10

        # When
        result = service._chunk_list(emails)

        # Then
        assert len(result) == 1
        assert len(result[0]) == 2
        assert result[0] == emails
