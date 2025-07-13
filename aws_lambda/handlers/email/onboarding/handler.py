import json

from service import send_onboarding_email


def lambda_handler(event: dict, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        emails = body["emails"]

        if not emails:
            raise ValueError("이메일이 안왔습니다.")
        result = send_onboarding_email(emails)
        return {"status": "ok", "result": result}
