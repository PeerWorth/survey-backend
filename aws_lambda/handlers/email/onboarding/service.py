import logging
import os
from typing import cast

import boto3
from jinja2 import Environment, FileSystemLoader, select_autoescape
from mypy_boto3_ses.client import SESClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def render_onboarding_template() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, "template")

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.get_template("content.html")
    html = template.render(unsubscribe_link="https://olass.co.kr/unsubscribe")

    return html


def send_onboarding_email(emails: list[list]):
    to_addresses = [email[1] for email in emails]

    ses = cast(SESClient, boto3.client("ses", region_name="ap-northeast-2"))
    try:
        response = ses.send_email(
            Source="noreply@olass.co.kr",
            Destination={"ToAddresses": to_addresses},
            Message={
                "Subject": {"Data": "🎉 olass에 오신 걸 환영합니다!"},
                "Body": {"Html": {"Data": render_onboarding_template()}},
            },
        )
        logger.info(f"SES 이메일을 성공적으로 보냈습니다. MessageId={response.get('MessageId')}")
        return response
    except Exception as e:
        logger.exception(f"SES send_email failed: {str(e)}")
        raise
