from test.fixtures.test_asset_model import AssetTestData
from uuid import uuid4

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.module.asset.model import Job, JobGroup, SalaryStat, UserProfile, UserSalary


@pytest.fixture
def job_group_factory(session: AsyncSession):
    async def _create(name: str = "개발") -> JobGroup:
        group = JobGroup(name=name)
        session.add(group)
        await session.commit()
        await session.refresh(group)
        return group

    return _create


@pytest.fixture
def job_factory(session: AsyncSession, job_group_factory):
    async def _create(name: str = "파이썬 개발자", group: JobGroup | None = None) -> Job:
        new_group = group or await job_group_factory()
        job = Job(group_id=new_group.id, name=name)
        session.add(job)
        await session.commit()
        await session.refresh(job)
        return job

    return _create


@pytest.fixture
def salary_stat_factory(session: AsyncSession):
    async def _create(job: Job, experience: int = 2, avg: int = 60000000) -> SalaryStat:
        stat = SalaryStat(job_id=job.id, experience=experience, avg=avg)
        session.add(stat)
        await session.commit()
        await session.refresh(stat)
        return stat

    return _create


@pytest.fixture
def user_salary_factory(session: AsyncSession):
    async def _create(job: Job, user_id: int = 1, experience: int = 2, salary: int = 50000000, uid=None) -> UserSalary:
        uid = uid or uuid4()
        us = UserSalary(
            id=uid,
            user_id=user_id,
            job_id=job.id,
            experience=experience,
            salary=salary,
        )
        session.add(us)
        await session.commit()
        await session.refresh(us)
        return us

    return _create


@pytest.fixture
def user_profile_factory(session: AsyncSession):
    async def _create(
        user_salary: UserSalary,
        age: int = 27,
        save_rate: int = 50,
        has_car: bool = False,
        monthly_rent: bool = True,
    ) -> UserProfile:
        profile = UserProfile(
            salary_id=user_salary.id.bytes,
            age=age,
            save_rate=save_rate,
            has_car=has_car,
            monthly_rent=monthly_rent,
        )
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
        return profile

    return _create


@pytest.fixture
def asset_data_builder(
    job_group_factory,
    job_factory,
    salary_stat_factory,
    user_salary_factory,
    user_profile_factory,
):
    class AssetDataBuilder:
        async def build(self) -> AssetTestData:
            group = await job_group_factory()
            job = await job_factory(group=group)
            stat = await salary_stat_factory(job)
            us = await user_salary_factory(job)
            profile = await user_profile_factory(us)
            return AssetTestData(
                job_group=group,
                job=job,
                salary_stat=stat,
                user_salary=us,
                user_profile=profile,
            )

    return AssetDataBuilder()
