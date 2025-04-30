from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.asset.v1.schemas.salary import UserSalaryPostRequest
from app.module.asset.model import UserSalary
from app.module.asset.repositories.user_salary_repository import UserSalaryRepository


class AssetService:
    def __init__(
        self,
        user_salary_repo: UserSalaryRepository = Depends(),
    ):
        self.user_salary_repo = user_salary_repo

    async def save_user_salary(self, user_salary_request: UserSalaryPostRequest) -> bool:
        user_salary = UserSalary(**user_salary_request.model_dump())
        saved = await self.user_salary_repo.save(user_salary)
        return True if saved else False

    async def get_jobs(self, session: AsyncSession):

        pass
