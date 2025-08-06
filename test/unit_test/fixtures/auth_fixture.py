import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.module.auth.model import User, UserConsent

from .base import BaseFactory


class UserFactory(BaseFactory):
    """사용자 팩토리"""

    async def create(self, email: str = "test@example.com") -> User:  # type: ignore
        user = User(email=email)
        return await self._save_and_refresh(user)


class UserConsentFactory(BaseFactory):
    """사용자 동의 팩토리"""

    async def create(self, user: User, event: str = "privacy_policy", agree: bool = True) -> UserConsent:  # type: ignore
        consent = UserConsent(user_id=user.id, event=event, agree=agree)
        return await self._save_and_refresh(consent)


class AuthDataBuilder:
    """인증 테스트 데이터 빌더"""

    def __init__(self, user_factory: UserFactory, user_consent_factory: UserConsentFactory):
        self._user_factory = user_factory
        self._user_consent_factory = user_consent_factory

    async def build(self):
        user = await self._user_factory.create()
        consent = await self._user_consent_factory.create(user)
        return {
            "user": user,
            "user_consent": consent,
        }


# pytest fixture 정의
@pytest.fixture
def user_factory(session: AsyncSession) -> UserFactory:
    return UserFactory(session)


@pytest.fixture
def user_consent_factory(session: AsyncSession) -> UserConsentFactory:
    return UserConsentFactory(session)


@pytest.fixture
def auth_data_builder(user_factory: UserFactory, user_consent_factory: UserConsentFactory) -> AuthDataBuilder:
    return AuthDataBuilder(user_factory, user_consent_factory)
