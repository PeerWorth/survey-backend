from fastapi import APIRouter, Depends, status

from app.api.asset.v1.dependencies.rate_limiter import salary_rate_limit_guard
from app.api.asset.v1.schemas.asset_schema import (
    JobsGetResponse,
    SalaryInfo,
    UserCarRankResponse,
    UserProfilePostRequest,
    UserSalaryInfo,
    UserSalaryPostRequest,
    UserSalaryPostResponse,
)
from app.common.schemas.base_schema import BaseReponse
from app.module.asset.model import SalaryStat
from app.module.asset.services.asset_service import AssetService

asset_router = APIRouter(prefix="/v1")


@asset_router.get("/jobs", summary="직무 데이터 반환", response_model=list[JobsGetResponse])
async def get_jobs(
    asset_service: AssetService = Depends(),
) -> list[JobsGetResponse]:
    jobs = await asset_service.get_jobs() or []

    return [
        JobsGetResponse(
            job_id=job.id,
            name=job.name,
        )
        for job in jobs
    ]


@asset_router.post(
    "/salary",
    summary="사용자 정보 입력 후 연봉 비교 결과 반환",
    response_model=UserSalaryPostResponse | BaseReponse,
    dependencies=[Depends(salary_rate_limit_guard)],
)
async def submit_user_salary(
    request_data: UserSalaryPostRequest,
    asset_service: AssetService = Depends(),
) -> UserSalaryPostResponse | BaseReponse:
    await asset_service.save_user_salary(request_data)

    # TODO: 차트 데이터 응답, 기획 미완성으로 대기중
    job_stat: SalaryStat | None = await asset_service.get_job_salary(request_data.job_id, request_data.experience)

    if not job_stat:
        return BaseReponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="저장 후, job_id + experience 와 매칭되는 데이터가 없습니다.",
        )

    return UserSalaryPostResponse(
        user=UserSalaryInfo(experience=request_data.experience, salary=request_data.salary),
        stat=SalaryInfo(
            experience=request_data.experience, lower=job_stat.lower, avg=job_stat.avg, upper=job_stat.upper
        ),
    )


@asset_router.post("/profile", response_model=UserCarRankResponse, summary="사용자 소비 패턴 입력 후 소비 등급 반환")
async def submit_user_profile(
    request_data: UserProfilePostRequest,
    asset_service: AssetService = Depends(),
) -> BaseReponse:
    await asset_service.save_user_profile(request_data)

    # TODO: 소비 패턴 별 등급 기획 마무리 시 변경 예정
    car_rank: str = asset_service.get_user_rank()

    return UserCarRankResponse(car=car_rank)
