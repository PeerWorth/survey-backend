"""Lambda 테스트를 위한 Mock Fixture"""

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_bigquery_client():
    """Google BigQuery Client Mock"""
    mock_client = MagicMock()
    mock_client.insert_rows_json = MagicMock(return_value=[])  # 성공 시 빈 리스트 반환
    return mock_client


@pytest.fixture
def mock_user_repository():
    """UserRepository Mock for Lambda"""
    return AsyncMock()


@pytest.fixture
def mock_trigger_repository():
    """TriggerRepository Mock for Lambda"""
    return AsyncMock()


@pytest.fixture
def mock_lambda_session():
    """Lambda DB Session Mock"""
    session = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_sns_client():
    """AWS SNS Client Mock"""
    mock_client = MagicMock()
    mock_client.publish = MagicMock(return_value={"MessageId": "test-message-id"})
    return mock_client
