import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.v1.schemas.user_schema import UserEmailRequest
from app.module.asset.repositories.user_salary_repository import UserSalaryRepository
from app.module.auth.enums import UserConsentEventEnum
from app.module.auth.errors.user_error import (
    ConsentCreationFailedError,
    SalaryAlreadyLinkedError,
    SalaryRecordNotFoundError,
    UserCreationFailedError,
)
from app.module.auth.model import User, UserConsent
from app.module.auth.repositories.user_consent_repository import UserConsentRepository
from app.module.auth.repositories.user_repository import UserRepository
from database.dependency import get_mysql_session_router


# TODO: 역할/책임 + 상태 Docstring 작성
class UserService:
    def __init__(
        self,
        user_repo: UserRepository = Depends(),
        user_salary_repo: UserSalaryRepository = Depends(),
        user_consent_repo: UserConsentRepository = Depends(),
        session: AsyncSession = Depends(get_mysql_session_router),
    ):
        self.user_repo = user_repo
        self.user_consent_repo = user_consent_repo
        self.user_salary_repo = user_salary_repo
        self.session = session

    async def save_user_with_marketing(self, user_email_request: UserEmailRequest) -> bool:
        data = user_email_request.model_dump()

        uid: uuid.UUID = data.pop("unique_id")
        email: str = data["email"]
        agree: bool = data["agree"]

        async with self.session.begin():
            salary_record = await self.user_salary_repo.get_by_uuid(uid)
            if not salary_record:
                raise SalaryRecordNotFoundError()
            if salary_record.user_id:
                raise SalaryAlreadyLinkedError()

            user = User(email=email)
            self.session.add(user)
            await self.session.flush()
            if not user.id:
                raise UserCreationFailedError()

            consent = UserConsent(user_id=user.id, event=UserConsentEventEnum.MARKETING, agree=agree)
            self.session.add(consent)
            await self.session.flush()
            if not consent.id:
                raise ConsentCreationFailedError()

            salary_record.user_id = user.id
            self.session.add(salary_record)

        return True
