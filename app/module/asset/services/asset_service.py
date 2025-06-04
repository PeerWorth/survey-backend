import uuid

from fastapi import Depends

from app.api.asset.v1.constant import SALARY_THOUSAND_WON
from app.api.asset.v1.schemas.asset_schema import UserProfilePostRequest, UserSalaryPostRequest
from app.module.asset.enums import CarRank
from app.module.asset.errors.asset_error import NoMatchJobSalary, NoMatchUserSalary
from app.module.asset.model import Job, SalaryStat, UserProfile, UserSalary
from app.module.asset.repositories.job_repository import JobRepository
from app.module.asset.repositories.salary_stat_repository import SalaryStatRepository
from app.module.asset.repositories.user_profile_repository import UserProfileRepository
from app.module.asset.repositories.user_salary_repository import UserSalaryRepository


# TODO: 역할/책임 + 상태 Docstring 작성
class AssetService:
    def __init__(
        self,
        user_salary_repo: UserSalaryRepository = Depends(),
        user_profile_repo: UserProfileRepository = Depends(),
        salary_stat_repo: SalaryStatRepository = Depends(),
        job_repo: JobRepository = Depends(),
    ):
        self.user_salary_repo = user_salary_repo
        self.user_profile_repo = user_profile_repo
        self.salary_stat_repo = salary_stat_repo
        self.job_repo = job_repo

    async def get_jobs(self) -> list[Job] | None:
        return await self.job_repo.gets()

    async def save_user_salary(self, user_salary_request: UserSalaryPostRequest) -> bool:
        data = user_salary_request.model_dump()

        uid: uuid.UUID = data.pop("unique_id")

        data["id"] = uid.bytes
        data["salary"] = data["salary"] * SALARY_THOUSAND_WON
        user_salary = UserSalary(**data)

        saved = await self.user_salary_repo.save(user_salary)
        return bool(saved)

    async def get_user_profile(self, unique_id: uuid.UUID) -> UserProfile | None:
        salary_id = unique_id.bytes
        return await self.user_profile_repo.get_by_salary_id(salary_id)

    async def save_user_profile(self, user_profile_request: UserProfilePostRequest) -> bool:
        data = user_profile_request.model_dump()
        uid: uuid.UUID = data.pop("unique_id")

        data["salary_id"] = uid.bytes

        user_profile = UserProfile(**data)
        saved = await self.user_profile_repo.save(user_profile)
        return bool(saved)

    async def get_job_salary(self, job_id: int, experience: int) -> SalaryStat | None:
        return await self.salary_stat_repo.get_by_job_id_experience(job_id, experience)

    async def get_user_car(self, user_profile_id: uuid.UUID, save_rate: int) -> str:
        user_salary: UserSalary | None = await self.user_salary_repo.get_by_uuid(user_profile_id)
        if not user_salary:
            raise NoMatchUserSalary()

        user_total_asset = int(user_salary.salary * (save_rate * 0.01) * 5 * 0.3)  # 유저 연봉 * 저축률 * 5년 * 30%

        return CarRank.get_car_rank(user_total_asset)

    async def get_user_percentage(self, user_profile_id: uuid.UUID, save_rate: int) -> int:
        user_salary: UserSalary | None = await self.user_salary_repo.get_by_uuid(user_profile_id)
        if not user_salary:
            raise NoMatchUserSalary()

        job_salary: SalaryStat | None = await self.salary_stat_repo.get_by_job_id_experience(
            user_salary.job_id, user_salary.experience
        )
        if not job_salary:
            raise NoMatchJobSalary()

        user_asset = int(user_salary.salary * save_rate * 0.01)

        percentage = 100 - int((user_asset / job_salary.avg) * 100)

        return max(0, min(percentage, 100))
