from fastapi import APIRouter, Depends, status

from app.api.auth.v1.schemas.user_schema import UserEmailRequest
from app.common.schemas.base_schema import BaseReponse
from app.module.auth.errors.user_error import (
    ConsentCreationFailedError,
    SalaryAlreadyLinkedError,
    SalaryRecordNotFoundError,
    UserCreationFailedError,
)
from app.module.auth.services.user_service import UserService

auth_router = APIRouter(prefix="/v1")


@auth_router.post("/email", summary="유저 이메일과 동의 약관 저장", response_model="")
async def submit_user_email(
    request_data: UserEmailRequest,
    user_service: UserService = Depends(),
):
    try:
        await user_service.save_user_with_marketing(request_data)
        return BaseReponse(status_code=status.HTTP_201_CREATED, detail="가입 성공")
    except SalaryRecordNotFoundError:
        raise BaseReponse(status.HTTP_404_NOT_FOUND, detail="연봉 기록을 찾을 수 없습니다.")
    except SalaryAlreadyLinkedError:
        raise BaseReponse(status.HTTP_400_BAD_REQUEST, detail="이미 연결된 연봉 기록입니다.")
    except (UserCreationFailedError, ConsentCreationFailedError):
        raise BaseReponse(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="서버 오류로 처리에 실패했습니다.")
