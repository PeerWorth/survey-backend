import asyncio

from aws_lambda.handlers.email.onboarding.repository import OnboardingRepository
from aws_lambda.handlers.email.onboarding.service import send_onboarding_email
from aws_lambda.shared.db_config import get_session


def lambda_handler(event, context):
    return asyncio.run(run_handler())


async def run_handler():
    session = await get_session()
    try:
        repo = OnboardingRepository(session)
        emails = await repo.get_agree_user_emails()
        result = send_onboarding_email(emails)
        return {"status": "ok", "result": result}
    finally:
        await session.close()
