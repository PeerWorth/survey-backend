from sqlalchemy.future import select

from app.common.repository.abstract_repository import BaseRepository
from app.module.asset.model import JobGroup


class JobGroupRepository(BaseRepository):
    async def save(self, instance: JobGroup, refresh=False) -> JobGroup | None:
        self.session.add(instance)
        return await self.commit_and_optional_refresh(instance, refresh)

    async def get(self, jog_group_id: int) -> JobGroup | None:
        return await self._get_by_id(JobGroup, jog_group_id)

    async def get_by_name(self, name: str) -> JobGroup | None:
        query = select(JobGroup).where(JobGroup.name == name)
        result = await self.session.execute(query)
        return result.scalars().first()
