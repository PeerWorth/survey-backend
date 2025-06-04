import uuid

import pytest

from app.api.asset.v1.schemas.asset_schema import UserProfilePostRequest, UserSalaryPostRequest
from app.module.asset.services.asset_service import AssetService


@pytest.mark.asyncio
class TestAssetService:
    @pytest.fixture(autouse=True)
    def _prepare(self, session):
        self.service = AssetService()

    async def test_get_user_car(self):
        uid = uuid.uuid4()

        await self.service.save_user_salary(UserSalaryPostRequest(unique_id=uid, job_id=1, experience=2, salary=5000))

        await self.service.save_user_profile(
            UserProfilePostRequest(unique_id=uid, age=30, save_rate=50, has_car=False, monthly_rent=True)
        )

        car = await self.service.get_user_car(uid, 50)
        assert isinstance(car, str)
