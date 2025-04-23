from sqlalchemy.ext.asyncio import AsyncSession

from app.module.asset.dto import SalarySubmissionData
from app.module.asset.repository.salary_submission_repository import SalarySubmissionRepository


class SalaryService:
    async def save_salary_submission(self, session: AsyncSession, submission_data: SalarySubmissionData) -> bool:
        saved = await SalarySubmissionRepository.save(session, submission_data)
        return True if saved else False
