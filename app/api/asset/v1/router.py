from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.asset.v1.rate_limiter import salary_rate_limit_guard
from app.api.asset.v1.schema import BaseReponse, SubmissionPostRequest
from app.module.asset.dependencies.salary_dependency import get_salary_service
from app.module.asset.services.salary_service import SalaryService
from database.dependency import get_mysql_session_router

asset_router = APIRouter(prefix="/v1")


@asset_router.post(
    "/salary",
    summary="유저 연봉 정보를 등록합니다.",
    response_model=BaseReponse,
    dependencies=[Depends(salary_rate_limit_guard)],
)
async def submit_user_information(
    request_data: SubmissionPostRequest,
    session: AsyncSession = Depends(get_mysql_session_router),
    salary_service: SalaryService = Depends(get_salary_service),
) -> BaseReponse:
    saved = await salary_service.save_salary_submission(session, request_data)

    return (
        BaseReponse(status_code=status.HTTP_201_CREATED, detail="성공적으로 저장하였습니다.")
        if saved
        else BaseReponse(status_code=status.HTTP_400_BAD_REQUEST, detail="저장에 실패하였습니다.")
    )
