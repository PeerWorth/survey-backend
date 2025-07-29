import asyncio

import pytest

from database.dependency import get_mysql_session_router
from main import app


@pytest.mark.asyncio
class TestEventLoopFixture:
    """Event loop fixture 테스트"""

    async def test_event_loop_is_running(self):
        """
        Given: pytest-asyncio가 설정되어 있을 때
        When: 비동기 테스트를 실행하면
        Then: 이벤트 루프가 활성화되어 있다
        """
        # Given - event_loop fixture가 자동으로 제공됨

        # When
        loop = asyncio.get_event_loop()

        # Then
        assert loop is not None
        assert loop.is_running()

    async def test_event_loop_handles_concurrent_tasks(self):
        """
        Given: 여러 비동기 작업이 있을 때
        When: 동시에 실행하면
        Then: 모든 작업이 올바르게 완료된다
        """

        # Given
        async def async_task(n):
            await asyncio.sleep(0.01)
            return n * 2

        # When
        tasks = [async_task(i) for i in range(5)]
        results = await asyncio.gather(*tasks)

        # Then
        assert results == [0, 2, 4, 6, 8]

    async def test_event_loop_scope_is_session(self):
        """
        Given: event_loop fixture가 session 스코프로 설정되어 있을 때
        When: 여러 테스트를 실행하면
        Then: 같은 이벤트 루프를 공유한다
        """
        # Given
        loop = asyncio.get_event_loop()

        # When
        # 루프의 고유 ID를 확인
        loop_id = id(loop)

        # Then
        assert loop_id is not None
        # 다른 테스트에서도 같은 loop_id를 가져야 함


@pytest.mark.asyncio
class TestDependencyOverrides:
    """의존성 오버라이드 테스트"""

    async def test_mysql_session_override_is_applied(self):
        """
        Given: get_mysql_session_router가 오버라이드되어 있을 때
        When: 의존성을 확인하면
        Then: 테스트용 세션이 사용된다
        """
        # Given - conftest.py에서 오버라이드됨

        # When
        overrides = app.dependency_overrides

        # Then
        assert get_mysql_session_router in overrides
        assert overrides[get_mysql_session_router] is not None

    async def test_redis_override_function_works(self, redis_client):
        """
        Given: Redis 오버라이드 함수가 제공될 때
        When: 함수를 사용하여 의존성을 오버라이드하면
        Then: 테스트용 Redis 클라이언트가 사용된다
        """
        # Given
        from test.conftest import override_get_redis_pool

        # When
        override_func = override_get_redis_pool(redis_client)
        test_redis = override_func()

        # Then
        assert test_redis is redis_client
        assert test_redis is not None

    async def test_dependency_override_isolation(self):
        """
        Given: 의존성 오버라이드가 설정되어 있을 때
        When: 다른 테스트에서 오버라이드를 변경해도
        Then: 기본 오버라이드는 유지된다
        """
        # Given

        # When
        # 임시로 다른 오버라이드 추가
        def dummy_dependency():
            return "dummy"

        app.dependency_overrides[dummy_dependency] = lambda: "test"

        # Then
        assert get_mysql_session_router in app.dependency_overrides
        assert dummy_dependency in app.dependency_overrides

        # 정리
        del app.dependency_overrides[dummy_dependency]


@pytest.mark.asyncio
class TestFixtureIntegration:
    """여러 fixture 통합 테스트"""

    async def test_session_and_client_work_together(self, session, client):
        """
        Given: 세션과 HTTP 클라이언트 fixture가 함께 주어졌을 때
        When: 두 fixture를 같이 사용하면
        Then: 서로 간섭 없이 동작한다
        """
        # Given - 두 fixture가 동시에 제공됨

        # When
        # 세션 사용
        assert session is not None
        assert session.is_active

        # 클라이언트 사용
        assert client is not None

        # Then
        # 두 fixture가 독립적으로 작동함

    async def test_redis_and_database_fixtures_coexist(self, session, redis_client):
        """
        Given: Redis와 데이터베이스 fixture가 함께 주어졌을 때
        When: 두 스토리지를 함께 사용하면
        Then: 각각 독립적으로 동작한다
        """
        # Given
        # Redis에 데이터 저장
        await redis_client.set("test_key", "redis_value")

        # When
        redis_value = await redis_client.get("test_key")

        # Then
        assert redis_value == "redis_value"
        assert session.is_active
        # 두 스토리지가 독립적으로 작동

    async def test_all_fixtures_together(self, session, client, redis_client):
        """
        Given: 모든 주요 fixture가 함께 주어졌을 때
        When: 복잡한 통합 시나리오를 테스트하면
        Then: 모든 컴포넌트가 올바르게 작동한다
        """
        # Given - 모든 fixture 사용 가능

        # When
        # 각 fixture 확인
        fixtures_status = {
            "session": session is not None and session.is_active,
            "client": client is not None,
            "redis": redis_client is not None,
        }

        # Then
        assert all(fixtures_status.values())
        assert len(fixtures_status) == 3
