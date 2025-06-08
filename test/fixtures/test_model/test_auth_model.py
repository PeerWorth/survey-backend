from dataclasses import dataclass

from app.module.auth.model import User, UserConsent


@dataclass
class AuthTestData:
    user: User
    user_consent: UserConsent
