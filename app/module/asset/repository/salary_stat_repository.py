from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.module.asset.model import SalaryStat


class SalaryStatRepository:
    @classmethod
    async def save(cls, session: AsyncSession, salary_stat: SalaryStat):
        try:
            session.add(salary_stat)
            await session.commit()
            await session.refresh(salary_stat)
            return salary_stat
        except IntegrityError:
            await session.rollback()
            return None

    @classmethod
    async def get(cls, session: AsyncSession, job_id: int, experience: int) -> SalaryStat | None:
        query = select(SalaryStat).where(SalaryStat.job_id == job_id, SalaryStat.experience == experience)
        result = await session.execute(query)
        return result.scalars().first()
