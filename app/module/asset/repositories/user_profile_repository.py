from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert

from app.common.repository.abstract_repository import BaseRepository
from app.module.asset.model import UserProfile


class UserProfileRepository(BaseRepository):
    async def save(self, instance: UserProfile, refresh=False) -> UserProfile | None:
        self.session.add(instance)
        return await self.commit_and_optional_refresh(instance, refresh)

    async def get(self, id: int) -> UserProfile | None:
        return await self._get_by_id(UserProfile, id)

    async def get_by_salary_id(self, salary_id: bytes) -> UserProfile | None:
        stmt = select(UserProfile).where(UserProfile.salary_id == salary_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(self, instance: UserProfile) -> UserProfile | None:
        stmt = insert(UserProfile).values(
            salary_id=instance.salary_id,
            age=instance.age,
            save_rate=instance.save_rate,
            has_car=instance.has_car,
            monthly_rent=instance.monthly_rent,
        )

        stmt = stmt.on_duplicate_key_update(
            age=stmt.inserted.age,
            save_rate=stmt.inserted.save_rate,
            has_car=stmt.inserted.has_car,
            monthly_rent=stmt.inserted.monthly_rent,
            updated_at=stmt.inserted.updated_at,
        )

        await self.session.execute(stmt)
        await self.session.commit()

        return await self.get_by_salary_id(instance.salary_id)
