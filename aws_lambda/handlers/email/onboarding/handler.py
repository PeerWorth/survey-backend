import asyncio

from repository import OnboardingRepository
from service import send_onboarding_email
from shared.db_config import get_session


def lambda_handler(event, context):
    return asyncio.run(run_handler())


async def run_handler() -> dict:
    session = await get_session()
    try:
        repo = OnboardingRepository(session)
        emails = await repo.get_agree_user_emails()
        if len(emails) > 1:
            return {"status": "error", "result": "개발용이 아닙니다."}

        result = send_onboarding_email(emails)
        return {"status": "ok", "result": result}
    finally:
        await session.close()
