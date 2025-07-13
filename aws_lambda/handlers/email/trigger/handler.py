import asyncio
import concurrent.futures
from os import getenv

import boto3
from enums import EmailType
from service import EmailTargetService
from sns_publisher import SnsPublisher

SNS_TOPIC_ARN = getenv("SNS_TOPIC_ARN", "arn:aws:sns:ap-northeast-2:590184068466:olass-email")
REGION = getenv("AWS_REGION", "ap-northeast-2")
if not SNS_TOPIC_ARN:
    raise ValueError("SNS_TOPIC_ARN이 환경변수에 세팅되지 않았습니다.")

sns = boto3.client("sns", region_name=REGION)
sns_publisher = SnsPublisher(sns, SNS_TOPIC_ARN)


def lambda_handler(event, context):
    return asyncio.run(_lambda_handler(event, context))


async def _lambda_handler(event: dict, context):
    email_type_raw = event.get("email_type")
    if not email_type_raw:
        raise ValueError("이메일 타입을 정의해야만 합니다.")

    try:
        email_type = EmailType(email_type_raw)
    except ValueError:
        raise ValueError(f"지원하지 않는 이메일 타입입니다: {email_type_raw}")

    service = await EmailTargetService.create()
    user_emails_nested = await service.get_target_emails()

    def publish(batch):
        return sns_publisher.publish_email_batch(email_type.value, batch)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(publish, batch) for batch in user_emails_nested]
        concurrent.futures.wait(futures)

    return {
        "status": "ok",
        "total_sent_batch": len(user_emails_nested),
        "email_type": email_type.value,
    }
