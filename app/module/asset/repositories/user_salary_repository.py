from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.asset.model import UserSalary


class UserSalaryRepository:
    @classmethod
    async def save(cls, session: AsyncSession, UserSalary: UserSalary) -> UserSalary | None:
        try:
            session.add(UserSalary)
            await session.commit()
            await session.refresh(UserSalary)
            return UserSalary
        except IntegrityError:
            await session.rollback()
            return None
