import pytest


@pytest.mark.asyncio
class TestRedisFixture:
    """Redis fixture 테스트"""

    async def test_redis_client_connection(self, redis_client):
        # Given - redis_client fixture로 제공됨

        # When
        result = await redis_client.ping()

        # Then
        assert result is True

    async def test_redis_client_set_get(self, redis_client):
        # Given
        test_key = "test_key"
        test_value = "test_value"

        # When
        await redis_client.set(test_key, test_value)
        retrieved_value = await redis_client.get(test_key)

        # Then
        assert retrieved_value == test_value

    async def test_redis_client_cleanup(self, redis_client):
        # Given
        test_key = "cleanup_test"
        test_value = "value"
        await redis_client.set(test_key, test_value)

        # When
        exists = await redis_client.exists(test_key)

        # Then
        assert exists == 1

    async def test_int_redis_repository_stores_and_retrieves_integers(self, int_redis_repository):
        # Given
        test_key = "int_key"
        test_value = 42
        expire_seconds = 60

        # When
        set_result = await int_redis_repository.set(test_key, test_value, expire=expire_seconds)
        retrieved_value = await int_redis_repository.get(test_key)

        # Then
        assert set_result is True
        assert retrieved_value == test_value
        assert isinstance(retrieved_value, int)

    async def test_json_redis_repository_stores_and_retrieves_json_data(self, json_redis_repository):
        # Given
        test_key = "json_key"
        test_data = {"name": "test", "value": 123, "items": ["a", "b", "c"]}
        expire_seconds = 60

        # When
        set_result = await json_redis_repository.set(test_key, test_data, expire=expire_seconds)
        retrieved_data = await json_redis_repository.get(test_key)

        # Then
        assert set_result is True
        assert retrieved_data == test_data
        assert isinstance(retrieved_data, dict)
        assert retrieved_data["items"] == ["a", "b", "c"]

    async def test_redis_repository_returns_none_for_non_existent_key(self, general_redis_repository):
        # Given
        non_existent_key = "this_key_does_not_exist"

        # When
        result = await general_redis_repository.get(non_existent_key)

        # Then
        assert result is None

    async def test_redis_repository_with_nx_option_prevents_overwrite(self, general_redis_repository):
        # Given
        test_key = "nx_test_key"
        original_value = "original"
        new_value = "new"
        await general_redis_repository.set(test_key, original_value, expire=60)

        # When
        set_result = await general_redis_repository.set(test_key, new_value, expire=60, nx=True)
        current_value = await general_redis_repository.get(test_key)

        # Then
        assert set_result is None  # nx=True로 인한 설정 실패
        assert current_value == original_value
