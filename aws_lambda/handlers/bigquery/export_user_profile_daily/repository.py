from datetime import date

from shared.asset_model import Job, JobGroup, UserProfile, UserSalary
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_profiles(self) -> list[dict]:
        today = date.today()

        stmt = (
            select(
                UserSalary.user_id,
                JobGroup.name.label("job_group"),  # type: ignore[attr-defined]
                Job.name.label("job"),  # type: ignore[attr-defined]
                UserSalary.experience,
                UserProfile.age,
                UserProfile.save_rate,
                UserProfile.has_car,
                UserProfile.monthly_rent,
            )
            .join(UserProfile, UserProfile.salary_id == UserSalary.id)
            .join(Job, Job.id == UserSalary.job_id)
            .join(JobGroup, JobGroup.id == Job.group_id)
            .where(
                or_(
                    func.date(UserProfile.created_at) == today,
                    func.date(UserProfile.updated_at) == today,
                    func.date(UserProfile.deleted_at) == today,
                )
            )
        )

        result = await self.session.execute(stmt)
        return [
            {
                "event_date": today.isoformat(),
                "user_id": row.user_id,
                "job_group": row.job_group,
                "job": row.job,
                "experience": row.experience,
                "age": row.age,
                "save_rate": row.save_rate,
                "has_car": row.has_car,
                "monthly_rent": row.monthly_rent,
            }
            for row in result.all()
        ]
