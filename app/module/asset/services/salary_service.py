from sqlalchemy.ext.asyncio import AsyncSession

from app.api.asset.v1.schemas.salary import UserSalaryPostRequest
from app.module.asset.model import UserSalary
from app.module.asset.repositories.user_salary_repository import UserSalaryRepository


class SalaryService:
    async def save_user_salary(self, session: AsyncSession, submission_data: UserSalaryPostRequest) -> bool:
        salary_submission = UserSalary(**submission_data.model_dump())
        saved = await UserSalaryRepository.save(session, salary_submission)
        return True if saved else False
