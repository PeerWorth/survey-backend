from fastapi import APIRouter

auth_router = APIRouter(prefix="/v1")


@auth_router.post()
async def submit_user_email():
    # TODO: 유저 이메일 입력
    pass
