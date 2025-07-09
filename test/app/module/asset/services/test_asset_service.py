import uuid
from test.fixtures.test_full_fixture import FullTestDataBuilder
from test.fixtures.test_model.test_full_model import FullTestData

import pytest

from app.api.asset.v1.constant import SALARY_THOUSAND_WON
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

    async def test_get_user_car(self, full_test_data_builder: FullTestDataBuilder):
        table_data: FullTestData = await full_test_data_builder.build()

        uid = uuid.uuid4()
        user_salary_input = table_data.user_salary.salary // SALARY_THOUSAND_WON
        await self.service.save_user_salary(
            UserSalaryPostRequest(
                uniqueId=uid,
                jobId=table_data.job.id,
                experience=table_data.user_salary.experience,
                salary=user_salary_input,
            )
        )

        await self.service.save_user_profile(
            UserProfilePostRequest(uniqueId=uid, age=30, saveRate=50, hasCar=False, isMonthlyRent=True)
        )

        car = await self.service.get_user_car(uid, 50)
        assert isinstance(car, str)

    async def test_get_user_percentage(self, full_test_data_builder: FullTestDataBuilder):
        table_data: FullTestData = await full_test_data_builder.build()

        uid = uuid.uuid4()
        user_salary_input = table_data.user_salary.salary // SALARY_THOUSAND_WON
        await self.service.save_user_salary(
            UserSalaryPostRequest(
                uniqueId=uid,
                jobId=table_data.job.id,
                experience=table_data.user_salary.experience,
                salary=user_salary_input,
            )
        )

        await self.service.save_user_profile(
            UserProfilePostRequest(uniqueId=uid, age=30, saveRate=50, hasCar=False, isMonthlyRent=True)
        )

        percentage = await self.service.get_user_percentage(uid, 50)
        assert isinstance(percentage, int)

    async def test_get_user_percentage_over_0(self, full_test_data_builder: FullTestDataBuilder):
        table_data: FullTestData = await full_test_data_builder.build()

        uid = uuid.uuid4()

        await self.service.save_user_salary(
            UserSalaryPostRequest(
                uniqueId=uid, jobId=table_data.job.id, experience=table_data.user_salary.experience, salary=100_000
            )
        )

        await self.service.save_user_profile(
            UserProfilePostRequest(uniqueId=uid, age=30, saveRate=99, hasCar=False, isMonthlyRent=True)
        )

        percentage = await self.service.get_user_percentage(uid, 99)
        assert percentage == 0
