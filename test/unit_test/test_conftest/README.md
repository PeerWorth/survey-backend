# conftest.py Fixture 테스트

이 폴더는 `test/conftest.py`에서 정의된 fixture들을 테스트하는 파일들을 담고 있습니다.

## 파일 구조

- `test_redis_fixtures.py` - Redis 관련 fixture 테스트

  - `redis_client` fixture
  - `general_redis_repository`, `int_redis_repository`, `json_redis_repository` fixture

- `test_database_fixtures.py` - 데이터베이스 관련 fixture 테스트

  - `session` fixture (MySQL 세션)
  - 테이블 생성/삭제, 트랜잭션 롤백, 테스트 격리

- `test_http_client_fixtures.py` - HTTP 클라이언트 fixture 테스트

  - `client` fixture (FastAPI AsyncClient)
  - HTTP 요청 처리, 헤더 전달, 다양한 content-type

- `test_integration_fixtures.py` - 통합 및 기타 fixture 테스트
  - `event_loop` fixture
  - 의존성 오버라이드 테스트
  - 여러 fixture 통합 사용

## 실행 방법

```bash
# 전체 conftest fixture 테스트 실행
poetry run pytest test/test_conftest

# 특정 fixture 테스트 실행
poetry run pytest test/test_conftest/test_redis_fixtures.py

# 특정 테스트 메서드 실행
poetry run pytest -k "test_redis_client_connection"
```

## 테스트 패턴

모든 테스트는 **Give-When-Then** 패턴을 따릅니다:

```python
async def test_example(self, fixture):
    """
    Given: 조건이 주어졌을 때
    When: 특정 동작을 수행하면
    Then: 예상 결과가 나타난다
    """
    # Given
    setup_data = "test_data"

    # When
    result = await fixture.some_operation(setup_data)

    # Then
    assert result == expected_value
```

## 주의사항

- 이 테스트들은 실제 Redis와 테스트 데이터베이스 연결이 필요합니다
- 각 테스트는 독립적으로 실행되며 데이터가 자동으로 정리됩니다
- fixture들은 `test/conftest.py`에서 정의되므로 해당 파일 수정 시 이 테스트들도 함께 확인해야 합니다
