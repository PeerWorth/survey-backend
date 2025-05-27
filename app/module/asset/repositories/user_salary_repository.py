import uuid

from sqlalchemy.future import select

from app.common.repository.abstract_repository import BaseRepository
from app.module.asset.model import UserSalary


class UserSalaryRepository(BaseRepository):
    async def save(self, instance: UserSalary) -> UserSalary | None:
        self.session.add(instance)
        return await self.commit_and_refresh(instance)

    async def get(self, salary_id: int) -> UserSalary | None:
        return await self._get_by_id(UserSalary, salary_id)

    async def get_by_uuid(self, uid: uuid.UUID) -> UserSalary | None:
        stmt = select(UserSalary).where(UserSalary.id == uid.bytes)
        result = await self.session.execute(stmt)
        return result.scalars().first()
