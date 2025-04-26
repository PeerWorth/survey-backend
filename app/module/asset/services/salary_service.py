from sqlalchemy.ext.asyncio import AsyncSession

from app.api.asset.v1.schema import SubmissionPostRequest
from app.module.asset.model import SalarySubmission
from app.module.asset.repositories.salary_submission_repository import SalarySubmissionRepository


class SalaryService:
    async def save_salary_submission(self, session: AsyncSession, submission_data: SubmissionPostRequest) -> bool:
        salary_submission = SalarySubmission(**submission_data.model_dump())
        saved = await SalarySubmissionRepository.save(session, salary_submission)
        return True if saved else False
