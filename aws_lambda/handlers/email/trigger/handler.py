import asyncio
import logging
from os import getenv

import boto3
import email_target_handlers.onboarding_handler  # noqa: F401[명시적 _registry 등록]
from enums import EmailType
from registry import get_email_target_handler
from sns_publisher import SnsPublisher

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


SNS_TOPIC_ARN = getenv("SNS_TOPIC_ARN", None)
REGION = getenv("AWS_REGION", "ap-northeast-2")
if not SNS_TOPIC_ARN:
    raise ValueError("SNS_TOPIC_ARN이 환경변수에 세팅되지 않았습니다.")

sns = boto3.client("sns", region_name=REGION)
sns_publisher = SnsPublisher(sns, SNS_TOPIC_ARN)


def lambda_handler(event, context):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        return loop.create_task(_lambda_handler(event, context))
    else:
        return loop.run_until_complete(_lambda_handler(event, context))


async def _lambda_handler(event: dict, context):
    email_type_raw = event.get("email_type")
    if not email_type_raw:
        raise ValueError("이메일 타입을 정의해야만 합니다.")

    try:
        email_type = EmailType(email_type_raw)
        logger.info(f"이메일 타입: {email_type}")
    except ValueError:
        raise ValueError(f"지원하지 않는 이메일 타입입니다: {email_type_raw}")

    handler = get_email_target_handler(email_type)
    user_emails_nested = await handler()

    logger.info(f"총 전송 메시지 개수 {len(user_emails_nested)}")

    for batch in user_emails_nested:
        sns_publisher.publish_email_batch(email_type.value, batch)

    logger.info(f"email_type: {email_type.value}, 총 {len(user_emails_nested)}개의 메시지를 SNS에 전달하였습니다.")

    return {
        "status": "ok",
        "total_sent_batch": len(user_emails_nested),
        "email_type": email_type.value,
    }
