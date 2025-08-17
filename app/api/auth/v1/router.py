from fastapi import APIRouter, Depends, status

from app.api.auth.v1.schemas.user_schema import UserEmailRequest
from app.common.docs.responses import COMMON_ERROR_RESPONSES
from app.common.schemas.base_schema import SuccessPostResponse
from app.module.auth.response import AUTH_ERROR_RESPONSES
from app.module.auth.services.user_service import UserService

auth_router = APIRouter(prefix="/v1")


@auth_router.post(
    "/email",
    summary="유저 이메일과 동의 약관 저장",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessPostResponse,
    responses={
        **COMMON_ERROR_RESPONSES,
        **AUTH_ERROR_RESPONSES,
    },
)
async def submit_user_email(
    request_data: UserEmailRequest,
    user_service: UserService = Depends(),
) -> SuccessPostResponse:
    await user_service.save_user_with_marketing(request_data)
    return SuccessPostResponse()
