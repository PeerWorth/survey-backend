import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.api.asset.v1.constant import SALARY_THOUSAND_WON
from app.api.asset.v1.schemas.asset_schema import UserProfilePostRequest, UserSalaryPostRequest
from app.module.asset.enums import CarRank
from app.module.asset.errors.asset_error import NoMatchJobSalary, NoMatchUserSalary
from app.module.asset.model import SalaryStat, UserProfile, UserSalary

# Fixtures imported via pytest plugin system
pytest_plugins = ["test.unit_test.fixtures.asset_mock_fixture"]


class TestGetJobSalary:
    @pytest.mark.asyncio
    async def test_get_job_salary_success(self, asset_service, mock_salary_stat_repo):
        # Given
        job_id = 1
        experience = 3
        salary_stat = SalaryStat(job_id=job_id, experience=experience, avg=70000000)
        mock_salary_stat_repo.get_by_job_id_experience.return_value = salary_stat

        # When
        result = await asset_service.get_job_salary(job_id, experience)

        # Then
        assert result == salary_stat
        mock_salary_stat_repo.get_by_job_id_experience.assert_called_once_with(job_id, experience)


class TestGetUserCar:
    @pytest.mark.asyncio
    async def test_car_rank_calculation(self, asset_service, mock_user_salary_repo):
        # Given
        user_profile_id = uuid.uuid4()
        save_rate = 50
        user_salary = UserSalary(
            id=user_profile_id.bytes,
            user_id=1,
            job_id=1,
            experience=3,
            salary=60000000,
        )
        mock_user_salary_repo.get_by_uuid.return_value = user_salary

        # When
        with patch.object(CarRank, "get_car_rank", return_value="중형차") as mock_get_car_rank:
            result = await asset_service.get_user_car(user_profile_id, save_rate)

        # Then
        assert result == "중형차"
        expected_asset = int(60000000 * 0.5 * 5 * 0.3)  # 45000000
        mock_get_car_rank.assert_called_once_with(expected_asset)

    @pytest.mark.asyncio
    async def test_no_user_salary_raises_error(self, asset_service, mock_user_salary_repo):
        # Given
        user_profile_id = uuid.uuid4()
        mock_user_salary_repo.get_by_uuid.return_value = None

        # When & Then
        with pytest.raises(NoMatchUserSalary):
            await asset_service.get_user_car(user_profile_id, 50)


class TestGetUserPercentage:
    @pytest.mark.asyncio
    async def test_percentage_calculation(self, asset_service, mock_user_salary_repo, mock_salary_stat_repo):
        # Given
        user_profile_id = uuid.uuid4()
        save_rate = 30
        user_salary = UserSalary(
            id=user_profile_id.bytes,
            user_id=1,
            job_id=1,
            experience=3,
            salary=50000000,
        )
        job_salary = SalaryStat(job_id=1, experience=3, avg=60000000)

        mock_user_salary_repo.get_by_uuid.return_value = user_salary
        mock_salary_stat_repo.get_by_job_id_experience.return_value = job_salary

        # When
        result = await asset_service.get_user_percentage(user_profile_id, save_rate)

        # Then
        user_asset = int(50000000 * 0.3)  # 15000000
        expected_percentage = 100 - int((user_asset / 60000000) * 100)  # 100 - 25 = 75
        assert result == expected_percentage

    @pytest.mark.asyncio
    async def test_percentage_bounds(self, asset_service, mock_user_salary_repo, mock_salary_stat_repo):
        # Given - 매우 높은 저축률로 상위 퍼센트를 초과하는 경우
        user_profile_id = uuid.uuid4()
        save_rate = 200  # 200% 저축률 (불가능하지만 테스트용)
        user_salary = UserSalary(
            id=user_profile_id.bytes,
            user_id=1,
            job_id=1,
            experience=3,
            salary=100000000,
        )
        job_salary = SalaryStat(job_id=1, experience=3, avg=50000000)

        mock_user_salary_repo.get_by_uuid.return_value = user_salary
        mock_salary_stat_repo.get_by_job_id_experience.return_value = job_salary

        # When
        result = await asset_service.get_user_percentage(user_profile_id, save_rate)

        # Then - 0과 100 사이로 제한됨
        assert result == 0  # max(0, min(percentage, 100))

    @pytest.mark.asyncio
    async def test_no_job_salary_raises_error(self, asset_service, mock_user_salary_repo, mock_salary_stat_repo):
        # Given
        user_profile_id = uuid.uuid4()
        user_salary = UserSalary(
            id=user_profile_id.bytes,
            user_id=1,
            job_id=1,
            experience=3,
            salary=50000000,
        )
        mock_user_salary_repo.get_by_uuid.return_value = user_salary
        mock_salary_stat_repo.get_by_job_id_experience.return_value = None

        # When & Then
        with pytest.raises(NoMatchJobSalary):
            await asset_service.get_user_percentage(user_profile_id, 30)


class TestGetUserProfile:
    @pytest.mark.asyncio
    async def test_get_user_profile_success(self, asset_service, mock_user_profile_repo):
        # Given
        unique_id = uuid.uuid4()
        user_profile = UserProfile(
            salary_id=unique_id.bytes,
            age=30,
            save_rate=40,
            has_car=True,
            is_monthly_rent=False,
        )
        mock_user_profile_repo.get_by_salary_id.return_value = user_profile

        # When
        result = await asset_service.get_user_profile(unique_id)

        # Then
        assert result == user_profile
        mock_user_profile_repo.get_by_salary_id.assert_called_once_with(unique_id.bytes)


class TestSaveUserSalary:
    @pytest.mark.asyncio
    async def test_save_user_salary_success(self, asset_service, mock_user_salary_repo):
        # Given
        unique_id = uuid.uuid4()
        request = UserSalaryPostRequest(
            unique_id=unique_id,
            job_id=2,
            experience=5,
            salary=80000,  # 단위: 천원
        )
        mock_user_salary_repo.upsert.return_value = MagicMock(id=unique_id.bytes)

        # When
        result = await asset_service.save_user_salary(request)

        # Then
        assert result is True
        saved_salary = mock_user_salary_repo.upsert.call_args[0][0]
        assert saved_salary.id == unique_id.bytes
        assert saved_salary.salary == 80000 * SALARY_THOUSAND_WON  # 80000000
        assert saved_salary.job_id == 2
        assert saved_salary.experience == 5

    @pytest.mark.asyncio
    async def test_save_user_salary_duplicate_id_updates(self, asset_service, mock_user_salary_repo):
        # Given - 동일한 ID로 두 번 요청하는 경우
        unique_id = uuid.uuid4()

        # 첫 번째 요청
        first_request = UserSalaryPostRequest(
            unique_id=unique_id,
            job_id=1,
            experience=3,
            salary=50000,
        )

        # 두 번째 요청 (동일한 ID, 다른 데이터)
        second_request = UserSalaryPostRequest(
            unique_id=unique_id,
            job_id=2,
            experience=5,
            salary=80000,
        )

        mock_user_salary_repo.upsert.return_value = MagicMock(id=unique_id.bytes)

        # When - 첫 번째 저장
        result1 = await asset_service.save_user_salary(first_request)

        # When - 두 번째 저장 (업데이트)
        result2 = await asset_service.save_user_salary(second_request)

        # Then
        assert result1 is True
        assert result2 is True

        # upsert가 두 번 호출되었는지 확인
        assert mock_user_salary_repo.upsert.call_count == 2

        # 두 번째 호출의 데이터 확인
        second_call_salary = mock_user_salary_repo.upsert.call_args[0][0]
        assert second_call_salary.id == unique_id.bytes
        assert second_call_salary.salary == 80000 * SALARY_THOUSAND_WON
        assert second_call_salary.job_id == 2
        assert second_call_salary.experience == 5


class TestSaveUserProfile:
    @pytest.mark.asyncio
    async def test_save_user_profile_success(self, asset_service, mock_user_profile_repo, mock_user_salary_repo):
        # Given
        unique_id = uuid.uuid4()
        request = UserProfilePostRequest(
            unique_id=unique_id,
            age=28,
            save_rate=45,
            has_car=False,
            is_monthly_rent=True,
        )

        # UserSalary가 이미 존재한다고 가정
        mock_user_salary_repo.get_by_uuid.return_value = UserSalary(
            id=unique_id.bytes, user_id=1, job_id=1, experience=3, salary=50000000
        )
        mock_user_profile_repo.upsert.return_value = MagicMock(salary_id=unique_id.bytes)

        # When
        result = await asset_service.save_user_profile(request)

        # Then
        assert result is True
        saved_profile = mock_user_profile_repo.upsert.call_args[0][0]
        assert saved_profile.salary_id == unique_id.bytes
        assert saved_profile.age == 28
        assert saved_profile.save_rate == 45
        assert saved_profile.has_car is False
        assert saved_profile.is_monthly_rent is True

    @pytest.mark.asyncio
    async def test_save_user_profile_no_salary_raises_error(self, asset_service, mock_user_salary_repo):
        # Given - UserSalary가 존재하지 않는 경우
        unique_id = uuid.uuid4()
        request = UserProfilePostRequest(
            unique_id=unique_id,
            age=28,
            save_rate=45,
            has_car=False,
            is_monthly_rent=True,
        )
        mock_user_salary_repo.get_by_uuid.return_value = None

        # When & Then
        with pytest.raises(NoMatchUserSalary):
            await asset_service.save_user_profile(request)

    @pytest.mark.asyncio
    async def test_save_user_profile_duplicate_id_updates(
        self, asset_service, mock_user_profile_repo, mock_user_salary_repo
    ):
        # Given - 동일한 salary_id로 두 번 요청하는 경우
        unique_id = uuid.uuid4()

        # UserSalary가 이미 존재한다고 가정
        mock_user_salary_repo.get_by_uuid.return_value = UserSalary(
            id=unique_id.bytes, user_id=1, job_id=1, experience=3, salary=50000000
        )

        # 첫 번째 요청
        first_request = UserProfilePostRequest(
            unique_id=unique_id,
            age=25,
            save_rate=30,
            has_car=False,
            is_monthly_rent=True,
        )

        # 두 번째 요청 (동일한 ID, 다른 데이터)
        second_request = UserProfilePostRequest(
            unique_id=unique_id,
            age=28,
            save_rate=45,
            has_car=True,
            is_monthly_rent=False,
        )

        mock_user_profile_repo.upsert.return_value = MagicMock(salary_id=unique_id.bytes)

        # When - 첫 번째 저장
        result1 = await asset_service.save_user_profile(first_request)

        # When - 두 번째 저장 (업데이트)
        result2 = await asset_service.save_user_profile(second_request)

        # Then
        assert result1 is True
        assert result2 is True

        # upsert가 두 번 호출되었는지 확인
        assert mock_user_profile_repo.upsert.call_count == 2

        # 두 번째 호출의 데이터 확인
        second_call_profile = mock_user_profile_repo.upsert.call_args[0][0]
        assert second_call_profile.salary_id == unique_id.bytes
        assert second_call_profile.age == 28
        assert second_call_profile.save_rate == 45
        assert second_call_profile.has_car is True
        assert second_call_profile.is_monthly_rent is False
