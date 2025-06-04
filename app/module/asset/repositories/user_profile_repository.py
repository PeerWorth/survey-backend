from sqlalchemy import select

from app.common.repository.abstract_repository import BaseRepository
from app.module.asset.model import UserProfile


class UserProfileRepository(BaseRepository):
    async def save(self, instance: UserProfile) -> UserProfile | None:
        self.session.add(instance)
        return await self.commit_and_refresh(instance)

    async def get(self, id: int) -> UserProfile | None:
        return await self._get_by_id(UserProfile, id)

    async def get_by_salary_id(self, salary_id: bytes) -> UserProfile | None:
        stmt = select(UserProfile).where(UserProfile.salary_id == salary_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
