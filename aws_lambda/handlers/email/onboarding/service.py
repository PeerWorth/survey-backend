import os
from typing import cast

import boto3
from jinja2 import Environment, FileSystemLoader, select_autoescape
from mypy_boto3_ses.client import SESClient


def render_onboarding_template() -> str:
    base_dir = os.path.dirname(__file__)
    template_dir = os.path.abspath(os.path.join(base_dir, "..", "..", "..", "shared"))

    env = Environment(loader=FileSystemLoader([template_dir, base_dir]), autoescape=select_autoescape(["html"]))

    template = env.get_template("template.html")
    return template.render(subject="olass에 오신 걸 환영합니다!")


def send_onboarding_email(emails: list[str]):
    if not emails:
        return

    ses = cast(SESClient, boto3.client("ses", region_name="ap-northeast-2"))
    rendered_html = render_onboarding_template()

    response = ses.send_email(
        Source="noreply@olass.co.kr",
        Destination={"ToAddresses": emails},
        Message={
            "Subject": {"Data": "🎉 olass에 오신 걸 환영합니다!"},
            "Body": {"Html": {"Data": rendered_html}},
        },
    )
    return response
