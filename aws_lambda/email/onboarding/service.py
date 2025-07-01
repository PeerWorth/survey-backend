import os
from typing import cast

import boto3
from jinja2 import Template
from mypy_boto3_ses.client import SESClient


def render_template(name: str, start_link: str) -> str:
    template_path = os.path.join(os.path.dirname(__file__), "template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()
    return Template(html).render(name=name, start_link=start_link)


def send_onboarding_email(to_email: str, name: str):
    ses = cast(SESClient, boto3.client("ses", region_name="ap-northeast-2"))

    rendered_html = render_template(name, start_link="https://www.olass.co.kr")

    response = ses.send_email(
        Source="noreply@olass.co.kr",
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": "🎉 olass에 오신 걸 환영합니다!"},
            "Body": {"Html": {"Data": rendered_html}, "Text": {"Data": f"{name}님, olass에 오신 것을 환영합니다!"}},
        },
    )
    return response
