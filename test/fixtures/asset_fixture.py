from test.fixtures.base import BaseFactory
from uuid import UUID, uuid4

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.module.asset.model import Job, JobGroup, SalaryStat, UserProfile, UserSalary
from app.module.auth.model import User


class JobGroupFactory(BaseFactory):
    """직군 팩토리"""

    async def create(self, name: str = "개발") -> JobGroup:  # type: ignore
        group = JobGroup(name=name)
        return await self._save_and_refresh(group)


class JobFactory(BaseFactory):
    """직무 팩토리"""

    def __init__(self, session: AsyncSession, job_group_factory: JobGroupFactory):
        super().__init__(session)
        self._job_group_factory = job_group_factory

    async def create(self, name: str = "파이썬 개발자", group: JobGroup | None = None) -> Job:  # type: ignore
        if group is None:
            group = await self._job_group_factory.create()

        job = Job(group_id=group.id, name=name)
        return await self._save_and_refresh(job)


class SalaryStatFactory(BaseFactory):
    """급여 통계 팩토리"""

    async def create(self, job: Job, experience: int = 2, avg: int = 60000000) -> SalaryStat:  # type: ignore
        stat = SalaryStat(job_id=job.id, experience=experience, avg=avg)
        return await self._save_and_refresh(stat)


class UserSalaryFactory(BaseFactory):
    """사용자 급여 팩토리"""

    async def create(  # type: ignore
        self,
        user: User,
        job: Job,
        experience: int = 2,
        salary: int = 50000000,
        uid: UUID | None = None,
    ) -> UserSalary:
        uid = uid or uuid4()
        user_salary = UserSalary(
            id=uid.bytes,
            user_id=user.id,
            job_id=job.id,
            experience=experience,
            salary=salary,
        )
        return await self._save_and_refresh(user_salary)


class UserProfileFactory(BaseFactory):
    """사용자 프로필 팩토리"""

    async def create(  # type: ignore
        self,
        user_salary: UserSalary,
        age: int = 27,
        save_rate: int = 50,
        has_car: bool = False,
        monthly_rent: bool = True,
    ) -> UserProfile:
        profile = UserProfile(
            salary_id=user_salary.id,
            age=age,
            save_rate=save_rate,
            has_car=has_car,
            monthly_rent=monthly_rent,
        )
        return await self._save_and_refresh(profile)


class AssetDataBuilder:
    """자산 테스트 데이터 빌더"""

    def __init__(
        self,
        user_factory,
        job_group_factory: JobGroupFactory,
        job_factory: JobFactory,
        salary_stat_factory: SalaryStatFactory,
        user_salary_factory: UserSalaryFactory,
        user_profile_factory: UserProfileFactory,
    ):
        self._user_factory = user_factory
        self._job_group_factory = job_group_factory
        self._job_factory = job_factory
        self._salary_stat_factory = salary_stat_factory
        self._user_salary_factory = user_salary_factory
        self._user_profile_factory = user_profile_factory

    async def build(self):
        user = await self._user_factory.create()
        group = await self._job_group_factory.create()
        job = await self._job_factory.create(group=group)
        stat = await self._salary_stat_factory.create(job)
        user_salary = await self._user_salary_factory.create(user=user, job=job)
        profile = await self._user_profile_factory.create(user_salary)

        return {
            "job_group": group,
            "job": job,
            "salary_stat": stat,
            "user_salary": user_salary,
            "user_profile": profile,
        }


# pytest fixture 정의
@pytest.fixture
def job_group_factory(session: AsyncSession) -> JobGroupFactory:
    return JobGroupFactory(session)


@pytest.fixture
def job_factory(session: AsyncSession, job_group_factory: JobGroupFactory) -> JobFactory:
    return JobFactory(session, job_group_factory)


@pytest.fixture
def salary_stat_factory(session: AsyncSession) -> SalaryStatFactory:
    return SalaryStatFactory(session)


@pytest.fixture
def user_salary_factory(session: AsyncSession) -> UserSalaryFactory:
    return UserSalaryFactory(session)


@pytest.fixture
def user_profile_factory(session: AsyncSession) -> UserProfileFactory:
    return UserProfileFactory(session)


@pytest.fixture
def asset_data_builder(
    user_factory,
    job_group_factory: JobGroupFactory,
    job_factory: JobFactory,
    salary_stat_factory: SalaryStatFactory,
    user_salary_factory: UserSalaryFactory,
    user_profile_factory: UserProfileFactory,
) -> AssetDataBuilder:
    return AssetDataBuilder(
        user_factory,
        job_group_factory,
        job_factory,
        salary_stat_factory,
        user_salary_factory,
        user_profile_factory,
    )
