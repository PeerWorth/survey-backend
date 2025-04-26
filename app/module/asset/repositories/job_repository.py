from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.module.asset.model import Job


class JobRepository:
    @classmethod
    async def save(cls, session: AsyncSession, job: Job) -> Job | None:
        session.add(job)

        try:
            await session.commit()
            await session.refresh(job)
            return job
        except IntegrityError:
            await session.rollback()
            return None

    @classmethod
    async def get(cls, session: AsyncSession, group_id: int, name: str) -> Job | None:
        query = select(Job).where(Job.name == name, Job.group_id == group_id)
        result = await session.execute(query)
        return result.scalars().first()
