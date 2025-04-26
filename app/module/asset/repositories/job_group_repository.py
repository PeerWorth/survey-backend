from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.module.asset.model import JobGroup


class JobGroupRepository:
    @classmethod
    async def save(cls, session: AsyncSession, job_group: JobGroup) -> JobGroup | None:
        session.add(job_group)

        try:
            await session.commit()
            await session.refresh(job_group)
            return job_group
        except IntegrityError as e:
            print(e)
            await session.rollback()
            return None

    @classmethod
    async def get(cls, session: AsyncSession, name: str) -> JobGroup | None:
        query = select(JobGroup).where(JobGroup.name == name)
        result = await session.execute(query)
        return result.scalars().first()
