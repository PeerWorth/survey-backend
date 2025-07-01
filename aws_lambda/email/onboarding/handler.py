from service import send_onboarding_email

if __name__ == "__main__":
    to_email = "kcw2371@gmail.com"
    name = "김채욱"

    res = send_onboarding_email(to_email, name)
    print("Email sent:", res["MessageId"])
