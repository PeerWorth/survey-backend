from typing import cast

import boto3
from mypy_boto3_ses.client import SESClient

from app.email.render import render_template


def send_test_email(to_email: str):
    ses = cast(SESClient, boto3.client("ses", region_name="ap-northeast-2"))

    html = render_template(template_name="marketing/onboarding.html", context={"site_url": "https://www.olass.co.kr"})

    response = ses.send_email(
        Source="kcw2371@gmail.com",
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": "[Olass] 자산 관리, 지금 시작해도 늦지 않았습니다."},
            "Body": {"Html": {"Data": html}, "Text": {"Data": "Plaintext fallback for test email."}},
        },
    )

    return response
