from sqlalchemy.future import select

from app.common.repository.abstract_repository import BaseRepository
from app.module.asset.model import Job


class JobRepository(BaseRepository):
    async def save(self, instance: Job, refresh=False) -> Job | None:
        self.session.add(instance)
        return await self.commit_and_optional_refresh(instance, refresh)

    async def get(self, job_id: int) -> Job | None:
        return await self._get_by_id(Job, job_id)

    async def gets(self) -> list[Job]:
        stmt = select(Job)
        result = await self.session.execute(stmt)
        jobs = result.scalars().all()
        return jobs

    async def find_by_group_and_name(self, group_id: int, name: str) -> Job | None:
        stmt = select(Job).where(Job.group_id == group_id, Job.name == name)
        res = await self.session.execute(stmt)
        return res.scalars().first()
