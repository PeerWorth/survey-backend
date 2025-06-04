import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.module.auth.model import User, UserConsent


@pytest.fixture
async def user(session: AsyncSession) -> User:
    test_user = User(email="test@example.com")
    session.add(test_user)
    await session.commit()
    await session.refresh(test_user)
    return test_user


@pytest.fixture
async def user_consent(session: AsyncSession, user: User) -> UserConsent:
    consent = UserConsent(user_id=user.id, event="privacy_policy", agree=True)
    session.add(consent)
    await session.commit()
    await session.refresh(consent)
    return consent


@pytest.fixture(scope="function")
async def setup_all(
    user,
    user_consent,
):
    pass
