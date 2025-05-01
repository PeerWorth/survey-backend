from fastapi import Depends

from app.api.asset.v1.schemas.asset_schema import UserSalaryPostRequest
from app.module.asset.model import Job, UserSalary
from app.module.asset.repositories.job_repository import JobRepository
from app.module.asset.repositories.user_salary_repository import UserSalaryRepository


class AssetService:
    def __init__(
        self,
        user_salary_repo: UserSalaryRepository = Depends(),
        job_repo: JobRepository = Depends(),
    ):
        self.user_salary_repo = user_salary_repo
        self.job_repo = job_repo

    async def save_user_salary(self, user_salary_request: UserSalaryPostRequest) -> bool:
        user_salary = UserSalary(**user_salary_request.model_dump())
        saved = await self.user_salary_repo.save(user_salary)
        return True if saved else False

    async def get_jobs(self) -> list[Job] | None:
        return await self.job_repo.gets()
