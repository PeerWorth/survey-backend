import uuid

from sqlalchemy.dialects.mysql import insert
from sqlalchemy.future import select

from app.common.repository.abstract_repository import BaseRepository
from app.module.asset.model import UserSalary


class UserSalaryRepository(BaseRepository):
    async def save(self, instance: UserSalary, refresh=True) -> UserSalary | None:
        self.session.add(instance)
        return await self.commit_and_optional_refresh(instance, refresh)

    async def get(self, salary_id: int) -> UserSalary | None:
        return await self._get_by_id(UserSalary, salary_id)

    async def get_by_uuid(self, uid: uuid.UUID) -> UserSalary | None:
        stmt = select(UserSalary).where(UserSalary.id == uid.bytes)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def upsert(self, instance: UserSalary) -> UserSalary | None:
        """
        Insert or update UserSalary record.
        If a record with the same id exists, update it; otherwise insert a new record.
        """
        stmt = insert(UserSalary).values(
            id=instance.id,
            user_id=instance.user_id,
            job_id=instance.job_id,
            experience=instance.experience,
            salary=instance.salary,
        )

        stmt = stmt.on_duplicate_key_update(
            user_id=stmt.inserted.user_id,
            job_id=stmt.inserted.job_id,
            experience=stmt.inserted.experience,
            salary=stmt.inserted.salary,
            updated_at=stmt.inserted.updated_at,
        )

        await self.session.execute(stmt)
        await self.session.commit()

        return await self.get_by_uuid(uuid.UUID(bytes=instance.id))
