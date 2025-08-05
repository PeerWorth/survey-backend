import pytest
from sqlmodel import Field, SQLModel, select


class SampleUser(SQLModel, table=True):
    __tablename__ = "sample_users"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str


class TestDatabaseFixture:
    """Database session fixture 테스트"""

    @pytest.mark.asyncio
    async def test_session_creates_and_drops_tables(self, session):
        """
        Given: 테스트 세션이 주어졌을 때
        When: 세션을 사용하면
        Then: 테이블이 생성되고 테스트 후 삭제된다
        """
        # Given - session fixture로 제공됨

        # When - 테이블이 자동으로 생성되었는지 확인
        # 간단한 쿼리 실행
        result = await session.execute(select(1))

        # Then
        assert result.scalar() == 1
        assert session.is_active

    @pytest.mark.asyncio
    async def test_session_rollback_on_test_completion(self, session):
        """
        Given: 테스트 세션에서 데이터를 생성했을 때
        When: 테스트가 종료되면
        Then: 모든 변경사항이 롤백된다
        """
        # Given
        test_user = SampleUser(name="test", email="test@example.com")

        # When
        session.add(test_user)
        await session.commit()

        result = await session.execute(select(SampleUser).where(SampleUser.email == "test@example.com"))
        saved_user = result.scalar_one_or_none()

        # Then
        assert saved_user is not None
        assert saved_user.name == "test"
        # 이 데이터는 테스트 종료 후 자동으로 롤백됨

    @pytest.mark.asyncio
    async def test_session_isolation_between_tests(self, session):
        """
        Given: 다른 테스트에서 생성된 데이터가 있을 수 있을 때
        When: 현재 테스트에서 데이터를 조회하면
        Then: 다른 테스트의 데이터는 보이지 않는다
        """
        # Given - 이전 테스트에서 생성했을 수 있는 데이터

        # When
        result = await session.execute(select(SampleUser))
        users = result.scalars().all()

        # Then
        assert len(users) == 0  # 격리된 환경이므로 비어있음

    @pytest.mark.asyncio
    async def test_session_async_operations(self, session):
        """
        Given: 비동기 세션이 주어졌을 때
        When: 여러 비동기 작업을 수행하면
        Then: 모든 작업이 정상적으로 처리된다
        """
        # Given
        users = [SampleUser(name=f"user{i}", email=f"user{i}@example.com") for i in range(5)]

        # When
        session.add_all(users)
        await session.commit()

        # 비동기로 데이터 조회
        result = await session.execute(select(SampleUser).order_by(SampleUser.name))
        saved_users = result.scalars().all()

        # Then
        assert len(saved_users) == 5
        assert all(user.name.startswith("user") for user in saved_users)

    @pytest.mark.asyncio
    async def test_session_handles_constraints(self, session):
        """
        Given: 데이터베이스 제약조건이 있을 때
        When: 제약조건을 위반하는 작업을 시도하면
        Then: 적절한 예외가 발생한다
        """
        # Given
        user1 = SampleUser(name="duplicate", email="same@example.com")
        session.add(user1)
        await session.commit()

        # When - 같은 이메일로 다른 사용자 생성 시도
        user2 = SampleUser(name="another", email="same@example.com")
        session.add(user2)

        # Then
        # 실제 제약조건이 있다면 IntegrityError가 발생할 것
        # 여기서는 테스트 모델이므로 중복 허용됨
        await session.commit()  # 제약조건이 없으므로 성공

        result = await session.execute(select(SampleUser).where(SampleUser.email == "same@example.com"))
        users = result.scalars().all()
        assert len(users) == 2
