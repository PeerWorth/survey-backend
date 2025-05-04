from sqlalchemy.future import select

from app.common.repository.abstract_repository import BaseRepository
from app.module.asset.model import SalaryStat


class SalaryStatRepository(BaseRepository):
    async def save(self, instance: SalaryStat):
        self.session.add(instance)
        return await self.commit_and_refresh(instance)

    async def get(self, stat_id: int) -> SalaryStat | None:
        return await self._get_by_id(SalaryStat, stat_id)

    async def get_by_job_id_experience(self, job_id: int, experience: int) -> SalaryStat | None:
        stmt = select(SalaryStat).where(SalaryStat.job_id == job_id, SalaryStat.experience == experience)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def upsert_by_age_group(self, salary_stat: SalaryStat) -> SalaryStat | None:
        stmt = select(SalaryStat).where(
            SalaryStat.job_id.is_(None), SalaryStat.experience.is_(None), SalaryStat.age_group == salary_stat.age_group
        )
        result = await self.session.execute(stmt)
        existing = result.scalars().first()

        if existing:
            existing.lower = salary_stat.lower
            existing.avg = salary_stat.avg
            existing.upper = salary_stat.upper
            return await self.commit_and_refresh(existing)
        else:
            self.session.add(salary_stat)
            return await self.commit_and_refresh(salary_stat)
