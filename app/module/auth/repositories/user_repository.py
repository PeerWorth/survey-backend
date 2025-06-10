from app.common.repository.abstract_repository import BaseRepository
from app.module.auth.model import User


class UserRepository(BaseRepository):
    async def save(self, instance: User, refresh=False) -> User | None:
        self.session.add(instance)
        return await self.commit_and_optional_refresh(instance, refresh)

    async def get(self, job_id: int) -> User | None:
        return await self._get_by_id(User, job_id)
