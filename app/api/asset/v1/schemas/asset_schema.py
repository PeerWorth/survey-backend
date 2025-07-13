from pydantic import UUID4, BaseModel, ConfigDict, Field

from app.common.schemas.base_schema import BaseRequestModel, SuccessResponse


class JobItem(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "개발 전체",
            }
        },
    )


class JobResponseData(BaseModel):
    items: list[JobItem]


class JobSuccessResponse(SuccessResponse):
    data: JobResponseData  # type: ignore[pydanticIssue]


class UserSalaryPostRequest(BaseRequestModel):
    unique_id: UUID4
    job_id: int
    experience: int = Field(..., ge=0, le=10)
    salary: int = Field(..., gt=0, le=100_000)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "uniqueId": "2323f2ac-4066-4e32-9412-0321c70dd8dc",
                "jobId": 5,
                "experience": 2,
                "salary": 4500,
            }
        },
    )


class UserSalaryResponseData(BaseModel):
    user_experience: int
    user_salary: int
    job_salary: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": {"userExperience": 5, "userSalary": 5500, "jobSalary": 6000}},
    )


class UserSalaryResponse(SuccessResponse):
    data: UserSalaryResponseData  # type: ignore[pydanticIssue]


class UserProfilePostRequest(BaseRequestModel):
    unique_id: UUID4 = Field(..., description="클라이언트 uuid")
    age: int = Field(..., ge=18, le=50, description="나이")
    save_rate: int = Field(..., ge=0, le=100, description="저축률")
    has_car: bool = Field(..., description="자동차 보유")
    is_monthly_rent: bool = Field(..., description="월세 여부")

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "uniqueId": "2323f2ac-4066-4e32-9412-0321c70dd8dc",
                "age": 30,
                "saveRate": 50,
                "hasCar": False,
                "isMonthlyRent": True,
            }
        },
    )


class UserCarRankData(BaseModel):
    car: str = Field(..., description="자동차 등급")
    percentage: int = Field(..., description="비교 등급")

    model_config = ConfigDict(
        json_schema_extra={"example": {"car": "benz", "percentage": 25}},
    )


class UserCarRankResponse(SuccessResponse):
    data: UserCarRankData  # type: ignore[pydanticIssue]
