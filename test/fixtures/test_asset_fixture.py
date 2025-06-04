from uuid import uuid4

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.module.asset.model import Job, JobGroup, SalaryStat, UserProfile, UserSalary


@pytest.fixture
async def job_group(session: AsyncSession) -> JobGroup:
    group = JobGroup(name="개발")
    session.add(group)
    await session.commit()
    await session.refresh(group)
    return group


@pytest.fixture
async def job(session: AsyncSession, job_group: JobGroup) -> Job:
    job = Job(group_id=job_group.id, name="백엔드 개발자")
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job


@pytest.fixture
async def salary_stat(session: AsyncSession, job: Job) -> SalaryStat:
    stat = SalaryStat(job_id=job.id, experience=2, avg=60000000)
    session.add(stat)
    await session.commit()
    await session.refresh(stat)
    return stat


@pytest.fixture
async def user_salary(session: AsyncSession, job: Job) -> UserSalary:
    us = UserSalary(
        id=uuid4(),
        user_id=1,
        job_id=job.id,
        experience=2,
        salary=50000000,
    )
    session.add(us)
    await session.commit()
    await session.refresh(us)
    return us


@pytest.fixture
async def user_profile(session: AsyncSession, user_salary: UserSalary) -> UserProfile:
    profile = UserProfile(
        salary_id=user_salary.id.bytes,
        age=27,
        save_rate=50,
        has_car=False,
        monthly_rent=True,
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


@pytest.fixture(scope="function")
async def setup_all(
    job_group,
    job,
    salary_stat,
    user_salary,
    user_profile,
):
    pass
