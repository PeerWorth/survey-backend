from app.common.repository.abstract_repository import BaseRepository
from app.module.asset.model import UserProfile


class UserProfileRepository(BaseRepository):
    async def save(self, instance: UserProfile) -> UserProfile | None:
        self.session.add(instance)
        return await self.commit_and_refresh(instance)

    async def get(self, salary_id: int) -> UserProfile | None:
        return await self._get_by_id(UserProfile, salary_id)
