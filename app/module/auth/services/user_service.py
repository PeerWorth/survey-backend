import uuid

from fastapi import Depends

from app.api.auth.v1.schemas.user_schema import UserEmailRequest
from app.module.asset.model import UserSalary
from app.module.asset.repositories.user_salary_repository import UserSalaryRepository
from app.module.auth.enums import UserConsentEventEnum
from app.module.auth.errors.user_error import (
    ConsentCreationFailed,
    SalaryAlreadyLinked,
    SalaryNotFound,
    UserCreationFailed,
)
from app.module.auth.model import User, UserConsent
from app.module.auth.repositories.user_consent_repository import UserConsentRepository
from app.module.auth.repositories.user_repository import UserRepository


class UserService:
    def __init__(
        self,
        user_repo: UserRepository = Depends(),
        user_salary_repo: UserSalaryRepository = Depends(),
        user_consent_repo: UserConsentRepository = Depends(),
    ):
        self.user_repo = user_repo
        self.user_consent_repo = user_consent_repo
        self.user_salary_repo = user_salary_repo

    async def save_user_with_marketing(self, user_email_request: UserEmailRequest) -> bool:
        data = user_email_request.model_dump()

        uid: uuid.UUID = data.pop("unique_id")
        email: str = data["email"]
        agree: bool = data["agree"]

        salary_record: UserSalary | None = await self.user_salary_repo.get_by_uuid(uid)

        if not salary_record:
            raise SalaryNotFound()
        if salary_record.user_id:
            raise SalaryAlreadyLinked()

        new_user = User(email=email)
        user = await self.user_repo.save(new_user, True)
        if not user:
            raise UserCreationFailed()

        user_consent = UserConsent(user_id=user.id, event=UserConsentEventEnum.MARKETING, agree=agree)
        consent = await self.user_consent_repo.save(user_consent)
        if not consent:
            raise ConsentCreationFailed()

        salary_record.user_id = user.id
        await self.user_salary_repo.save(salary_record)

        return True
