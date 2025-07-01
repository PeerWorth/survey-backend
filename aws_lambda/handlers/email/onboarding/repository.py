from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aws_lambda.handlers.email.onboarding.constant import MARKETING
from aws_lambda.shared.auth_model import User, UserConsent


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
