from typing import Literal

from pydantic import UUID4, BaseModel, ConfigDict, Field


class UserSalaryPostRequest(BaseModel):
    schemaVersion: Literal["v1"] = "v1"
    unique_id: UUID4
    job_id: int
    experience: int = Field(..., ge=0, le=10)
    salary: int = Field(..., gt=0, le=1_000_000_000)


class UserSalaryPostResponse(BaseModel):
    user_experience: int
    user_salary: int
    job_salary: int

    model_config = ConfigDict(from_attributes=True)


class JobsGetResponse(BaseModel):
    job_id: int = Field(..., description="직무 id, 추후 POST 요청 시 선택한 직무 id 반환")
    name: str = Field(..., description="직무명")


class UserProfilePostRequest(BaseModel):
    unique_id: UUID4 = Field(..., description="클라이언트 uuid")
    age: int = Field(..., ge=18, le=50, description="나이")
    save_rate: int = Field(..., ge=0, le=100, description="저축률")
    has_car: bool = Field(..., description="자동차 보유")
    monthly_rent: bool = Field(..., description="웰세 여부")

    class Config:
        use_enum_values = True


class UserCarRankResponse(BaseModel):
    car: str = Field(..., description="자동차 등급")
    percentage: int = Field(..., description="비교 등급")
