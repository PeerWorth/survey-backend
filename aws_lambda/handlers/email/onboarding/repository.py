from constant import MARKETING
from shared.auth_model import User, UserConsent
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class OnboardingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_agree_user_emails(
        self,
    ) -> list[str]:
        stmt = (
            select(User.email)
            .join(UserConsent, User.id == UserConsent.user_id)
            .where(
                UserConsent.event == MARKETING,
                UserConsent.agree.is_(True),  # type: ignore
            )
        )

        result = await self.session.execute(stmt)
        emails = [row[0] for row in result.all()]
        return emails
