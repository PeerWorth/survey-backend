from service import send_onboarding_email


def lambda_handler(event: list[str], context):
    result = send_onboarding_email(event)
    return {"status": "ok", "result": result}
