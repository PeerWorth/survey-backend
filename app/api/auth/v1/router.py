from fastapi import APIRouter, Depends, status

from app.api.auth.v1.schemas.user_schema import UserEmailRequest
from app.common.schemas.base_schema import SuccessResponse
from app.module.auth.services.user_service import UserService

auth_router = APIRouter(prefix="/v1")


@auth_router.post("/email", summary="유저 이메일과 동의 약관 저장", response_model=SuccessResponse)
async def submit_user_email(
    request_data: UserEmailRequest,
    user_service: UserService = Depends(),
) -> SuccessResponse:
    await user_service.save_user_with_marketing(request_data)
    return SuccessResponse(code=status.HTTP_201_CREATED)
