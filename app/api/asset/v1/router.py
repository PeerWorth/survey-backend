from fastapi import APIRouter, Depends

from app.api.asset.v1.dependencies.rate_limiter import salary_rate_limit_guard
from app.api.asset.v1.schemas.asset_schema import (
    UserCarRankResponse,
    UserProfilePostRequest,
    UserSalaryPostRequest,
    UserSalaryPostResponse,
)
from app.module.asset.errors.asset_error import SalaryStatNotFound
from app.module.asset.model import Job, SalaryStat
from app.module.asset.services.asset_service import AssetService

asset_router = APIRouter(prefix="/v1")


@asset_router.get("/jobs", summary="직무 데이터 반환", response_model=list[Job])
async def get_jobs(
    asset_service: AssetService = Depends(),
) -> list[Job]:
    return await asset_service.get_jobs() or []


@asset_router.post(
    "/salary",
    summary="사용자 정보 입력 후 연봉 비교 결과 반환",
    response_model=UserSalaryPostResponse,
    dependencies=[Depends(salary_rate_limit_guard)],
)
async def submit_user_salary(
    request_data: UserSalaryPostRequest,
    asset_service: AssetService = Depends(),
) -> UserSalaryPostResponse:
    await asset_service.save_user_salary(request_data)

    job_stat: SalaryStat | None = await asset_service.get_job_salary(request_data.job_id, request_data.experience)
    if not job_stat:
        raise SalaryStatNotFound

    return UserSalaryPostResponse(
        user_experience=request_data.experience, user_salary=request_data.salary, job_salary=job_stat.avg
    )


@asset_router.post("/profile", response_model=UserCarRankResponse, summary="사용자 소비 패턴 입력 후 소비 등급 반환")
async def submit_user_profile(
    request_data: UserProfilePostRequest,
    asset_service: AssetService = Depends(),
) -> UserCarRankResponse:
    await asset_service.save_user_profile(request_data)

    car: str = await asset_service.get_user_rank(request_data.unique_id, request_data.save_rate)

    # TODO: cold-start 데이터가 완료가 되면, 퍼센티지를 반환하겠습니다.
    return UserCarRankResponse(car=car, percentage=1)
