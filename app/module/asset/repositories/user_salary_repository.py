from app.module.asset.model import UserSalary
from app.module.asset.repositories.abstract_repository import BaseRepository


class UserSalaryRepository(BaseRepository):
    async def save(self, instance: UserSalary) -> UserSalary | None:
        self.session.add(instance)
        return await self.commit_and_refresh(instance)

    async def get(self, salary_id: int) -> UserSalary | None:
        return await self._get_by_id(UserSalary, salary_id)
