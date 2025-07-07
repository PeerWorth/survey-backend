import asyncio
import json
from os import getenv
from typing import cast

import boto3
from enums import EmailType
from mypy_boto3_sqs.client import SQSClient
from service import TriggerService

SQS_QUEUE_URL = getenv("SQS_QUEUE_URL", None)
if not SQS_QUEUE_URL:
    raise ValueError("SQS URL이 세팅되지 않았습니다.")
REGION = getenv("AWS_REGION", "ap-northeast-2")


def lambda_handler(event, context):
    return asyncio.run(_lambda_handler(event, context))


async def _lambda_handler(event: dict, context):
    email_type = event.get("email_type")
    if not email_type:
        raise ValueError("이메일 타입을 정의해야만 합니다.")

    try:
        email_type = EmailType(email_type)
    except ValueError:
        raise ValueError(f"지원하지 않는 이메일 타입입니다: {email_type}")

    trigger_service = await TriggerService.create()
    user_emails_nested: list[list[tuple[int, str]]] = await trigger_service.get_target_emails()

    sqs = cast(SQSClient, boto3.client("sqs", region_name=REGION))

    for email_batch in user_emails_nested:
        message = {
            "email_type": EmailType.ONBOARDING.value,
            "emails": email_batch,
        }

        sqs.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=json.dumps(message))  # type: ignore

    return {"status": "ok", "total_sent_batch": len(user_emails_nested)}
