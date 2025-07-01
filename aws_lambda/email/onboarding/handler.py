from service import send_onboarding_email


def lambda_handler(event, context):
    to_email = event.get("email")
    name = event.get("name")

    if not to_email:
        raise ValueError("Missing required parameter: 'email'")
    if not name:
        raise ValueError("Missing required parameter: 'name'")

    result = send_onboarding_email(to_email, name)
    return {"status": "ok", "result": result}
