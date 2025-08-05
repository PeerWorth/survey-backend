"""Auth 모듈 테스트를 위한 Mock Fixture"""

from unittest.mock import AsyncMock

import pytest

from app.module.asset.repositories.user_salary_repository import UserSalaryRepository
from app.module.auth.repositories.user_consent_repository import UserConsentRepository
from app.module.auth.repositories.user_repository import UserRepository
from app.module.auth.services.user_service import UserService


@pytest.fixture
def mock_user_repo():
    """UserRepository Mock"""
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def mock_user_consent_repo():
    """UserConsentRepository Mock"""
    return AsyncMock(spec=UserConsentRepository)


@pytest.fixture
def mock_user_salary_repo_for_auth():
    """UserSalaryRepository Mock for auth module"""
    return AsyncMock(spec=UserSalaryRepository)


@pytest.fixture
def user_service(
    mock_user_repo,
    mock_user_consent_repo,
    mock_user_salary_repo_for_auth,
):
    """UserService with mocked dependencies"""
    return UserService(
        user_repo=mock_user_repo,
        user_consent_repo=mock_user_consent_repo,
        user_salary_repo=mock_user_salary_repo_for_auth,
    )
