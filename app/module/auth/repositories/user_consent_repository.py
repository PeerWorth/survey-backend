from app.common.repository.abstract_repository import BaseRepository
from app.module.auth.model import UserConsent


class UserConsentRepository(BaseRepository):
    async def save(self, instance: UserConsent) -> UserConsent | None:
        self.session.add(instance)
        return await self.commit_and_refresh(instance)

    async def get(self, job_id: int) -> UserConsent | None:
        return await self._get_by_id(UserConsent, job_id)
