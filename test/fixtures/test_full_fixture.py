from test.fixtures.test_model.test_full_model import FullTestData
from uuid import uuid4

import pytest


class FullTestDataBuilder:
    def __init__(
        self,
        user_factory,
        user_consent_factory,
        job_group_factory,
        job_factory,
        salary_stat_factory,
        user_salary_factory,
        user_profile_factory,
    ):
        self.user_factory = user_factory
        self.user_consent_factory = user_consent_factory
        self.job_group_factory = job_group_factory
        self.job_factory = job_factory
        self.salary_stat_factory = salary_stat_factory
        self.user_salary_factory = user_salary_factory
        self.user_profile_factory = user_profile_factory

    async def build(self) -> FullTestData:
        user = await self.user_factory()
        consent = await self.user_consent_factory(user)
        group = await self.job_group_factory()
        job = await self.job_factory(group=group)
        stat = await self.salary_stat_factory(job)
        salary = await self.user_salary_factory(user=user, job=job, uid=uuid4())
        profile = await self.user_profile_factory(salary)

        return FullTestData(
            user=user,
            user_consent=consent,
            job_group=group,
            job=job,
            salary_stat=stat,
            user_salary=salary,
            user_profile=profile,
        )


@pytest.fixture
def full_test_data_builder(
    user_factory,
    user_consent_factory,
    job_group_factory,
    job_factory,
    salary_stat_factory,
    user_salary_factory,
    user_profile_factory,
) -> FullTestDataBuilder:
    return FullTestDataBuilder(
        user_factory,
        user_consent_factory,
        job_group_factory,
        job_factory,
        salary_stat_factory,
        user_salary_factory,
        user_profile_factory,
    )
