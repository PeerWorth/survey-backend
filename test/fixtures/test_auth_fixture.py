from test.fixtures.test_model.test_auth_model import AuthTestData

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.module.auth.model import User, UserConsent


@pytest.fixture
def user_factory(session: AsyncSession):
    async def _create(email: str = "test@example.com") -> User:
        user = User(email=email)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    return _create


@pytest.fixture
def user_consent_factory(session: AsyncSession):
    async def _create(user: User, event: str = "privacy_policy", agree: bool = True) -> UserConsent:
        consent = UserConsent(user_id=user.id, event=event, agree=agree)
        session.add(consent)
        await session.commit()
        await session.refresh(consent)
        return consent

    return _create


@pytest.fixture
def auth_data_builder(user_factory, user_consent_factory):
    class AuthDataBuilder:
        async def build(self) -> AuthTestData:
            user = await user_factory()
            consent = await user_consent_factory(user)
            return AuthTestData(
                user=user,
                user_consent=consent,
            )

    return AuthDataBuilder()
