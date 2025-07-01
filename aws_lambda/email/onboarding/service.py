import os
from typing import cast

import boto3
from jinja2 import Environment, FileSystemLoader, select_autoescape
from mypy_boto3_ses.client import SESClient


def render_onboarding_template(name: str) -> str:
    base_dir = os.path.dirname(__file__)
    template_dir = os.path.join(base_dir, "..", "shared")

    env = Environment(loader=FileSystemLoader([template_dir, base_dir]), autoescape=select_autoescape(["html"]))

    template = env.get_template("template.html")
    return template.render(name=name, subject="olass에 오신 걸 환영합니다!")


def send_onboarding_email(to_email: str, name: str):
    ses = cast(SESClient, boto3.client("ses", region_name="ap-northeast-2"))

    rendered_html = render_onboarding_template(name)

    response = ses.send_email(
        Source="noreply@olass.co.kr",
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": "🎉 olass에 오신 걸 환영합니다!"},
            "Body": {"Html": {"Data": rendered_html}, "Text": {"Data": f"{name}님, olass에 오신 것을 환영합니다!"}},
        },
    )
    return response
