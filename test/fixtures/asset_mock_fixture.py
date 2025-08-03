"""Asset 모듈 테스트를 위한 Mock Fixture"""

from unittest.mock import AsyncMock

import pytest

from app.common.redis_repository.general_redis_repository import ListRedisRepository
from app.module.asset.repositories.job_repository import JobRepository
from app.module.asset.repositories.salary_stat_repository import SalaryStatRepository
from app.module.asset.repositories.user_profile_repository import UserProfileRepository
from app.module.asset.repositories.user_salary_repository import UserSalaryRepository
from app.module.asset.services.asset_service import AssetService


@pytest.fixture
def mock_user_salary_repo():
    """UserSalaryRepository Mock"""
    return AsyncMock(spec=UserSalaryRepository)


@pytest.fixture
def mock_user_profile_repo():
    """UserProfileRepository Mock"""
    return AsyncMock(spec=UserProfileRepository)


@pytest.fixture
def mock_salary_stat_repo():
    """SalaryStatRepository Mock"""
    return AsyncMock(spec=SalaryStatRepository)


@pytest.fixture
def mock_job_repo():
    """JobRepository Mock"""
    return AsyncMock(spec=JobRepository)


@pytest.fixture
def mock_job_cache_repo():
    """ListRedisRepository Mock for Job caching"""
    return AsyncMock(spec=ListRedisRepository)


@pytest.fixture
def asset_service(
    mock_user_salary_repo,
    mock_user_profile_repo,
    mock_salary_stat_repo,
    mock_job_repo,
    mock_job_cache_repo,
):
    """AssetService with mocked dependencies"""
    return AssetService(
        user_salary_repo=mock_user_salary_repo,
        user_profile_repo=mock_user_profile_repo,
        salary_stat_repo=mock_salary_stat_repo,
        job_repo=mock_job_repo,
        job_cache_repo=mock_job_cache_repo,
    )
