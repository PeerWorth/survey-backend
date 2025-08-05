from uuid import uuid4

import pytest


class FullTestDataBuilder:
    """전체 테스트 데이터 빌더"""

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
        self._user_factory = user_factory
        self._user_consent_factory = user_consent_factory
        self._job_group_factory = job_group_factory
        self._job_factory = job_factory
        self._salary_stat_factory = salary_stat_factory
        self._user_salary_factory = user_salary_factory
        self._user_profile_factory = user_profile_factory

    async def build(self):
        user = await self._user_factory.create()
        consent = await self._user_consent_factory.create(user)
        group = await self._job_group_factory.create()
        job = await self._job_factory.create(group=group)
        stat = await self._salary_stat_factory.create(job)
        salary = await self._user_salary_factory.create(user=user, job=job, uid=uuid4())
        profile = await self._user_profile_factory.create(salary)

        return {
            "user": user,
            "user_consent": consent,
            "job_group": group,
            "job": job,
            "salary_stat": stat,
            "user_salary": salary,
            "user_profile": profile,
        }


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
