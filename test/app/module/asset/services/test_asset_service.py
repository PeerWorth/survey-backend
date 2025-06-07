import uuid

import pytest

from app.api.asset.v1.schemas.asset_schema import UserProfilePostRequest, UserSalaryPostRequest
from app.module.asset.repositories.job_repository import JobRepository
from app.module.asset.repositories.salary_stat_repository import SalaryStatRepository
from app.module.asset.repositories.user_profile_repository import UserProfileRepository
from app.module.asset.repositories.user_salary_repository import UserSalaryRepository
from app.module.asset.services.asset_service import AssetService


@pytest.mark.asyncio
class TestAssetService:
    @pytest.fixture(autouse=True)
    def _prepare(self, session):
        self.service = AssetService(
            user_salary_repo=UserSalaryRepository(session),
            user_profile_repo=UserProfileRepository(session),
            salary_stat_repo=SalaryStatRepository(session),
            job_repo=JobRepository(session),
        )

    async def test_get_user_car(self, setup_all):
        uid = uuid.uuid4()

        saved = await self.service.save_user_salary(
            UserSalaryPostRequest(unique_id=uid, job_id=1, experience=2, salary=5000)
        )

        assert saved is True

        await self.service.save_user_profile(
            UserProfilePostRequest(unique_id=uid, age=30, save_rate=50, has_car=False, monthly_rent=True)
        )

        car = await self.service.get_user_car(uid, 50)
        assert isinstance(car, str)
