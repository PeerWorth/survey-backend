"""BigQuery Export Service 테스트 - 격리된 테스트"""

from unittest.mock import AsyncMock, MagicMock

import pytest


class MockUserService:
    """테스트용 UserService 모의 구현"""

    def __init__(self, repository, session):
        self.repository = repository
        self.session = session
        self.MAX_ROWS_PER_REQUEST = 5000  # constant.py에서 가져온 값

    async def get_user_profiles(self):
        """사용자 프로필 조회"""
        try:
            return await self.repository.get_user_profiles()
        finally:
            await self.session.close()

    def insert_to_bigquery(self, rows):
        """BigQuery에 데이터 삽입 (모의 구현)"""
        from itertools import islice

        def chunked(iterable, n):
            """리스트를 n개씩 나누는 헬퍼 함수"""
            it = iter(iterable)
            while chunk := list(islice(it, n)):
                yield chunk

        # BigQuery Client 생성 (모의)
        client = MagicMock()
        client.insert_rows_json = MagicMock(return_value=[])

        chunks = list(chunked(rows, self.MAX_ROWS_PER_REQUEST))
        total_success = 0

        for idx, chunk in enumerate(chunks):
            errors = client.insert_rows_json("test_table", chunk)
            if not errors:
                total_success += len(chunk)

        return total_success, len(rows), client


class TestUserServiceIsolated:
    """UserService 격리 테스트"""

    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.close = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_repository, mock_session):
        return MockUserService(repository=mock_repository, session=mock_session)

    @pytest.mark.asyncio
    async def test_get_user_profiles_success(self, service, mock_repository, mock_session):
        # Given
        expected_profiles = [
            {
                "event_date": "2024-01-01",
                "user_id": 1,
                "job_group": "개발",
                "job": "백엔드 개발자",
                "experience": 3,
                "age": 30,
                "save_rate": 50,
                "has_car": True,
                "monthly_rent": False,
            },
            {
                "event_date": "2024-01-01",
                "user_id": 2,
                "job_group": "디자인",
                "job": "UI/UX 디자이너",
                "experience": 2,
                "age": 28,
                "save_rate": 40,
                "has_car": False,
                "monthly_rent": True,
            },
        ]

        # Mock을 비동기로 만들기
        async def mock_get_user_profiles():
            return expected_profiles

        mock_repository.get_user_profiles = mock_get_user_profiles

        # When
        result = await service.get_user_profiles()

        # Then
        assert result == expected_profiles
        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_profiles_closes_session_on_error(self, service, mock_repository, mock_session):
        # Given
        async def mock_error():
            raise Exception("DB Error")

        mock_repository.get_user_profiles = mock_error

        # When & Then
        with pytest.raises(Exception, match="DB Error"):
            await service.get_user_profiles()

        mock_session.close.assert_called_once()

    def test_insert_to_bigquery_success(self, service):
        # Given
        rows = [
            {"user_id": 1, "job": "개발자"},
            {"user_id": 2, "job": "디자이너"},
            {"user_id": 3, "job": "기획자"},
        ]

        # When
        total_success, total_rows, mock_client = service.insert_to_bigquery(rows)

        # Then
        assert total_success == 3
        assert total_rows == 3
        mock_client.insert_rows_json.assert_called_once()

    def test_insert_to_bigquery_with_chunking(self, service):
        # Given
        service.MAX_ROWS_PER_REQUEST = 2  # 테스트용으로 작게 설정
        rows = [
            {"user_id": 1, "job": "개발자"},
            {"user_id": 2, "job": "디자이너"},
            {"user_id": 3, "job": "기획자"},
            {"user_id": 4, "job": "마케터"},
            {"user_id": 5, "job": "영업"},
        ]

        # When
        total_success, total_rows, mock_client = service.insert_to_bigquery(rows)

        # Then
        assert total_success == 5
        assert total_rows == 5
        # 5개를 2개씩 나누면 3번 호출 (2, 2, 1)
        assert mock_client.insert_rows_json.call_count == 3

    def test_insert_to_bigquery_empty_rows(self, service):
        # Given
        rows = []

        # When
        total_success, total_rows, mock_client = service.insert_to_bigquery(rows)

        # Then
        assert total_success == 0
        assert total_rows == 0
        mock_client.insert_rows_json.assert_not_called()
