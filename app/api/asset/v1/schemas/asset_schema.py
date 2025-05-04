from pydantic import UUID4, BaseModel, Field

from app.module.asset.enums import Gender


class UserSalaryPostRequest(BaseModel):
    unique_id: UUID4 = Field(..., description="클라이언트 uuid")
    job_id: int = Field(..., description="직무")
    experience: int = Field(..., ge=0, le=10, description="경력")
    salary: int = Field(..., gt=0, le=1_000_000_000, description="연봉")


class UserSalaryPostResponse(BaseModel):
    job_id: int = Field(..., description="직무 ID")
    experience: int = Field(int, description="경력")
    lower: int = Field(..., description="하위 연봉")
    avg: int = Field(..., description="평균 연봉")
    upper: int = Field(..., description="상위 연봉")

    class Config:
        orm_mode = True


class JobsGetResponse(BaseModel):
    job_id: int = Field(..., description="직무 id, 추후 POST 요청 시 선택한 직무 id 반환")
    name: str = Field(..., description="직무명")


class UserProfilePostRequest(BaseModel):
    unique_id: UUID4 = Field(..., description="클라이언트 uuid")
    age: int = Field(..., ge=18, le=50, description="나이")
    gender: Gender = Field(..., description="성별")
    save_rate: int = Field(..., ge=0, le=100, description="저축률")
    has_car: bool = Field(..., description="자동차 보유")

    class Config:
        use_enum_values = True
