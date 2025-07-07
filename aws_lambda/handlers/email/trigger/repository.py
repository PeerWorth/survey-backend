# from shared.auth_model import User, UserConsent
from constant import MARKETING
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aws_lambda.shared.auth_model import User, UserConsent


class TriggerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_agreed_emails(self) -> list[tuple[int, str]]:
        stmt = (
            select(User.id, User.email)
            .join(UserConsent, User.id == UserConsent.user_id)
            .where(
                UserConsent.event == MARKETING,
                UserConsent.agree.is_(True),  # type: ignore
            )
        )

        result = await self.session.execute(stmt)
        rows = result.all()
        return [(int(row[0]), str(row[1])) for row in rows]
