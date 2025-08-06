import uuid

import pytest

from app.api.auth.v1.schemas.user_schema import UserEmailRequest
from app.module.asset.model import UserSalary
from app.module.auth.enums import UserConsentEventEnum
from app.module.auth.errors.user_error import (
    ConsentCreationFailed,
    SalaryAlreadyLinked,
    SalaryNotFound,
    UserCreationFailed,
)
from app.module.auth.model import User, UserConsent

# Fixtures imported via pytest plugin system
pytest_plugins = ["test.unit_test.fixtures.auth_mock_fixture"]


class TestSaveUserWithMarketing:
    @pytest.mark.asyncio
    async def test_save_user_with_marketing_success(
        self, user_service, mock_user_repo, mock_user_salary_repo_for_auth, mock_user_consent_repo
    ):
        # Given
        unique_id = uuid.uuid4()
        email = "test@example.com"
        agree = True

        request = UserEmailRequest(
            unique_id=unique_id,
            email=email,
            agree=agree,
        )

        # UserSalary 레코드 (아직 user_id가 없는 상태)
        salary_record = UserSalary(
            id=unique_id.bytes,
            user_id=None,  # 아직 연결되지 않음
            job_id=1,
            experience=3,
            salary=50000000,
        )
        mock_user_salary_repo_for_auth.get_by_uuid.return_value = salary_record

        # 새로 생성될 User
        created_user = User(id=123, email=email)
        mock_user_repo.save.return_value = created_user

        # 생성될 UserConsent
        created_consent = UserConsent(
            id=1,
            user_id=created_user.id,
            event=UserConsentEventEnum.MARKETING,
            agree=agree,
        )
        mock_user_consent_repo.save.return_value = created_consent

        # When
        result = await user_service.save_user_with_marketing(request)

        # Then
        assert result is True

        # UserSalary 조회 확인
        mock_user_salary_repo_for_auth.get_by_uuid.assert_called_once_with(unique_id)

        # User 생성 확인
        saved_user = mock_user_repo.save.call_args[0][0]
        assert saved_user.email == email
        assert mock_user_repo.save.call_args[0][1] is True  # flush=True

        # UserConsent 생성 확인
        saved_consent = mock_user_consent_repo.save.call_args[0][0]
        assert saved_consent.user_id == created_user.id
        assert saved_consent.event == UserConsentEventEnum.MARKETING
        assert saved_consent.agree == agree

        # UserSalary에 user_id 연결 확인
        updated_salary = mock_user_salary_repo_for_auth.save.call_args[0][0]
        assert updated_salary.user_id == created_user.id

    @pytest.mark.asyncio
    async def test_salary_not_found(self, user_service, mock_user_salary_repo_for_auth):
        # Given
        unique_id = uuid.uuid4()
        request = UserEmailRequest(
            unique_id=unique_id,
            email="test@example.com",
            agree=True,
        )

        mock_user_salary_repo_for_auth.get_by_uuid.return_value = None

        # When & Then
        with pytest.raises(SalaryNotFound):
            await user_service.save_user_with_marketing(request)

    @pytest.mark.asyncio
    async def test_salary_already_linked(self, user_service, mock_user_salary_repo_for_auth):
        # Given
        unique_id = uuid.uuid4()
        request = UserEmailRequest(
            unique_id=unique_id,
            email="test@example.com",
            agree=True,
        )

        # 이미 user_id가 연결된 UserSalary
        salary_record = UserSalary(
            id=unique_id.bytes,
            user_id=100,  # 이미 연결됨
            job_id=1,
            experience=3,
            salary=50000000,
        )
        mock_user_salary_repo_for_auth.get_by_uuid.return_value = salary_record

        # When & Then
        with pytest.raises(SalaryAlreadyLinked):
            await user_service.save_user_with_marketing(request)

    @pytest.mark.asyncio
    async def test_user_creation_failed(self, user_service, mock_user_repo, mock_user_salary_repo_for_auth):
        # Given
        unique_id = uuid.uuid4()
        request = UserEmailRequest(
            unique_id=unique_id,
            email="test@example.com",
            agree=True,
        )

        salary_record = UserSalary(
            id=unique_id.bytes,
            user_id=None,
            job_id=1,
            experience=3,
            salary=50000000,
        )
        mock_user_salary_repo_for_auth.get_by_uuid.return_value = salary_record

        # User 생성 실패
        mock_user_repo.save.return_value = None

        # When & Then
        with pytest.raises(UserCreationFailed):
            await user_service.save_user_with_marketing(request)

    @pytest.mark.asyncio
    async def test_consent_creation_failed(
        self, user_service, mock_user_repo, mock_user_salary_repo_for_auth, mock_user_consent_repo
    ):
        # Given
        unique_id = uuid.uuid4()
        request = UserEmailRequest(
            unique_id=unique_id,
            email="test@example.com",
            agree=True,
        )

        salary_record = UserSalary(
            id=unique_id.bytes,
            user_id=None,
            job_id=1,
            experience=3,
            salary=50000000,
        )
        mock_user_salary_repo_for_auth.get_by_uuid.return_value = salary_record

        created_user = User(id=123, email="test@example.com")
        mock_user_repo.save.return_value = created_user

        # Consent 생성 실패
        mock_user_consent_repo.save.return_value = None

        # When & Then
        with pytest.raises(ConsentCreationFailed):
            await user_service.save_user_with_marketing(request)

    @pytest.mark.asyncio
    async def test_marketing_consent_disagree(
        self, user_service, mock_user_repo, mock_user_salary_repo_for_auth, mock_user_consent_repo
    ):
        # Given - 마케팅 동의하지 않는 경우
        unique_id = uuid.uuid4()
        email = "test@example.com"
        agree = False  # 동의하지 않음

        request = UserEmailRequest(
            unique_id=unique_id,
            email=email,
            agree=agree,
        )

        salary_record = UserSalary(
            id=unique_id.bytes,
            user_id=None,
            job_id=1,
            experience=3,
            salary=50000000,
        )
        mock_user_salary_repo_for_auth.get_by_uuid.return_value = salary_record

        created_user = User(id=123, email=email)
        mock_user_repo.save.return_value = created_user

        created_consent = UserConsent(
            id=1,
            user_id=created_user.id,
            event=UserConsentEventEnum.MARKETING,
            agree=agree,
        )
        mock_user_consent_repo.save.return_value = created_consent

        # When
        result = await user_service.save_user_with_marketing(request)

        # Then
        assert result is True

        # 동의하지 않은 경우에도 UserConsent는 저장됨 (agree=False로)
        saved_consent = mock_user_consent_repo.save.call_args[0][0]
        assert saved_consent.agree is False
