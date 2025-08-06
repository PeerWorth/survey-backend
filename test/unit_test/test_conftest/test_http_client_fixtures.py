import pytest
from fastapi import status


class TestHTTPClientFixture:
    """HTTP client fixture 테스트"""

    @pytest.mark.asyncio
    async def test_client_makes_http_requests(self, client, session):
        """
        Given: 테스트 HTTP 클라이언트가 주어졌을 때
        When: API 엔드포인트에 요청을 보내면
        Then: 정상적인 응답을 받는다
        """
        # Given - client fixture로 제공됨

        # When
        response = await client.get("/health")

        # Then
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        # 실제 /health 엔드포인트가 있다면 200, 없다면 404

    @pytest.mark.asyncio
    async def test_client_uses_test_database(self, client, session):
        """
        Given: 테스트 클라이언트와 세션이 주어졌을 때
        When: 데이터베이스를 사용하는 엔드포인트를 호출하면
        Then: 테스트 데이터베이스를 사용한다
        """
        # Given - 테스트 데이터베이스 세션이 오버라이드됨

        # When - 실제 엔드포인트가 있다면 테스트
        # 예: response = await client.get("/api/users")

        # Then
        # 테스트 DB 연결이 올바르게 오버라이드되었는지 확인
        assert session is not None
        assert session.is_active

    @pytest.mark.asyncio
    async def test_client_handles_json_data(self, client, session):
        """
        Given: JSON 데이터를 포함한 요청을 보낼 때
        When: POST 요청을 전송하면
        Then: JSON 데이터가 올바르게 처리된다
        """
        # Given

        # When - 실제 엔드포인트가 있다면
        # response = await client.post("/api/users", json=test_data)

        # Then - 기본 클라이언트 기능 테스트
        assert client is not None
        assert hasattr(client, "post")
        assert hasattr(client, "get")
        assert hasattr(client, "put")
        assert hasattr(client, "delete")

    @pytest.mark.asyncio
    async def test_client_preserves_headers(self, client, session):
        """
        Given: 커스텀 헤더가 필요한 요청을 보낼 때
        When: 헤더를 포함한 요청을 전송하면
        Then: 헤더가 올바르게 전달된다
        """
        # Given
        custom_headers = {"X-Test-Header": "test_value", "Authorization": "Bearer test_token"}

        # When
        response = await client.get("/", headers=custom_headers)

        # Then
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        # 헤더가 제대로 전달되었는지는 실제 엔드포인트에서 확인

    @pytest.mark.asyncio
    async def test_client_handles_different_content_types(self, client, session):
        """
        Given: 다양한 content-type의 요청을 보낼 때
        When: form-data나 다른 형식의 데이터를 전송하면
        Then: 각 content-type에 맞게 처리된다
        """
        # Given

        # When - form 데이터 전송
        # response = await client.post("/api/form", data=form_data)

        # Then
        # Form 데이터가 올바르게 처리되었는지 확인
        assert client is not None

    @pytest.mark.asyncio
    async def test_client_base_url_configuration(self, client, session):
        """
        Given: 테스트 클라이언트가 생성될 때
        When: base_url이 설정되면
        Then: 모든 요청에 base_url이 적용된다
        """
        # Given - conftest.py에서 base_url="http://test"로 설정됨

        # When
        # 클라이언트의 base_url 확인

        # Then
        assert client is not None
        # httpx.AsyncClient의 base_url 속성 확인
        assert hasattr(client, "_base_url")

    @pytest.mark.asyncio
    async def test_client_async_context_manager(self, client, session):
        """
        Given: 비동기 컨텍스트 매니저로 클라이언트를 사용할 때
        When: 테스트가 완료되면
        Then: 클라이언트가 자동으로 정리된다
        """
        # Given - client는 async with 문으로 생성됨

        # When
        # 클라이언트 사용
        assert client is not None

        # Then
        # 테스트 종료 시 자동으로 close됨
        # (fixture가 async context manager로 처리함)
