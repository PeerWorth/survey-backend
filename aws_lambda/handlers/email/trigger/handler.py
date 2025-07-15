import asyncio
from os import getenv

import boto3
from enums import EmailType
from registry import get_email_target_handler
from sns_publisher import SnsPublisher

SNS_TOPIC_ARN = getenv("SNS_TOPIC_ARN", "arn:aws:sns:ap-northeast-2:590184068466:olass-email")
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
    except ValueError:
        raise ValueError(f"지원하지 않는 이메일 타입입니다: {email_type_raw}")

    handler = get_email_target_handler(email_type)
    user_emails_nested = await handler()

    for batch in user_emails_nested:
        sns_publisher.publish_email_batch(email_type.value, batch)

    return {
        "status": "ok",
        "total_sent_batch": len(user_emails_nested),
        "email_type": email_type.value,
    }
