from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.asset.v1.dependencies.rate_limiter import salary_rate_limit_guard
from app.api.asset.v1.schemas.salary import BaseReponse, UserSalaryPostRequest
from app.module.asset.dependencies.asset_dependency import get_salary_service
from app.module.asset.services.asset_service import AssetService
from database.dependency import get_mysql_session_router

asset_router = APIRouter(prefix="/v1")


@asset_router.get(
    "/jobs",
    summary="직무 데이터 반환",
)
async def get_jobs(
    session: AsyncSession = Depends(get_mysql_session_router),
    asset_service: AssetService = Depends(get_salary_service),
):
    # TODO: 직무 데이터 반환

    pass


@asset_router.post(
    "/salary",
    summary="사용자 정보 입력 후 연봉 비교 결과 반환",
    response_model=BaseReponse,
    dependencies=[Depends(salary_rate_limit_guard)],
)
async def submit_user_salary(
    request_data: UserSalaryPostRequest,
    asset_service: AssetService = Depends(),
) -> BaseReponse:
    saved = await asset_service.save_user_salary(request_data)

    # TODO: 차트 데이터 응답, 기획 미완성으로 대기중

    return (
        BaseReponse(status_code=status.HTTP_201_CREATED, detail="성공적으로 저장하였습니다.")
        if saved
        else BaseReponse(status_code=status.HTTP_400_BAD_REQUEST, detail="저장에 실패하였습니다.")
    )


@asset_router.post(
    "/profile",
)
async def submit_user_profile():
    # TODO: 소비자 성향 데이터 입력
    pass
