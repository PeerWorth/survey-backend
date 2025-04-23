from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.asset.model import SalarySubmission


class SalarySubmissionRepository:
    @classmethod
    async def save(cls, session: AsyncSession, salary_submission: SalarySubmission) -> SalarySubmission | None:
        try:
            session.add(salary_submission)
            await session.commit()
            await session.refresh(salary_submission)
            return salary_submission
        except IntegrityError:
            await session.rollback()
            return None
