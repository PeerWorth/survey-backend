from typing import Annotated

from fastapi import APIRouter, Depends, Path
from pydantic import UUID4

from app.api.asset.v1.constant import SALARY_THOUSAND_WON
from app.api.asset.v1.schemas.asset_schema import (
    JobResponse,
    UserCarRankResponse,
    UserProfilePostRequest,
    UserSalaryPostRequest,
    UserSalaryPostResponse,
)
from app.module.asset.errors.asset_error import NoMatchUserProfile, NoUserProfileSaveRate, SalaryStatNotFound
from app.module.asset.model import SalaryStat, UserProfile
from app.module.asset.services.asset_service import AssetService

asset_router = APIRouter(prefix="/v1")


@asset_router.get("/jobs", summary="직무 데이터 반환", response_model=list[JobResponse])
async def get_jobs(
    asset_service: AssetService = Depends(),
) -> list[JobResponse]:
    jobs = await asset_service.get_jobs() or []
    return [JobResponse.model_validate(job) for job in jobs]


@asset_router.post(
    "/salary",
    summary="사용자 정보 입력 후 연봉 비교 결과 반환",
    response_model=UserSalaryPostResponse,
)
async def submit_user_salary(
    request_data: UserSalaryPostRequest,
    asset_service: AssetService = Depends(),
) -> UserSalaryPostResponse:
    await asset_service.save_user_salary(request_data)

    job_stat: SalaryStat | None = await asset_service.get_job_salary(request_data.job_id, request_data.experience)
    if not job_stat:
        raise SalaryStatNotFound

    job_salary_thousand = job_stat.avg // SALARY_THOUSAND_WON  # 천만원 단위

    return UserSalaryPostResponse(
        user_experience=request_data.experience, user_salary=request_data.salary, job_salary=job_salary_thousand
    )


@asset_router.post("/profile", response_model=UserCarRankResponse, summary="사용자 소비 패턴 입력 후 소비 등급 반환")
async def submit_user_profile(
    request_data: UserProfilePostRequest,
    asset_service: AssetService = Depends(),
) -> UserCarRankResponse:
    await asset_service.save_user_profile(request_data)

    car = await asset_service.get_user_car(request_data.unique_id, request_data.save_rate)
    percentage = await asset_service.get_user_percentage(request_data.unique_id, request_data.save_rate)
    return UserCarRankResponse(car=car, percentage=percentage)


@asset_router.get("/profile/{unique_id}", response_model=UserCarRankResponse, summary="유저 등급 공유 링크")
async def user_profile_link(
    unique_id: Annotated[UUID4, Path(description="유저 고유 UUID")],
    asset_service: AssetService = Depends(),
) -> UserCarRankResponse:
    user_profile: UserProfile | None = await asset_service.get_user_profile(unique_id)
    if user_profile is None:
        raise NoMatchUserProfile()

    if user_profile.save_rate is None:
        raise NoUserProfileSaveRate()

    car: str = await asset_service.get_user_car(unique_id, user_profile.save_rate)
    percentage: int = await asset_service.get_user_percentage(unique_id, user_profile.save_rate)

    return UserCarRankResponse(car=car, percentage=percentage)
