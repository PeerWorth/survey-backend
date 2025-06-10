from pydantic import UUID4, BaseModel, ConfigDict, Field


class JobResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "개발 전체",
            }
        },
    )


class UserSalaryPostRequest(BaseModel):
    unique_id: UUID4
    job_id: int
    experience: int = Field(..., ge=0, le=10)
    salary: int = Field(..., gt=0, le=100_000)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "unique_id": "2323f2ac-4066-4e32-9412-0321c70dd8dc",
                "job_id": 5,
                "experience": 2,
                "salary": 4500,
            }
        },
    )


class UserSalaryPostResponse(BaseModel):
    user_experience: int
    user_salary: int
    job_salary: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": {"user_experience": 5, "user_salary": 5500, "job_salary": 6000}},
    )


class UserProfilePostRequest(BaseModel):
    unique_id: UUID4 = Field(..., description="클라이언트 uuid")
    age: int = Field(..., ge=18, le=50, description="나이")
    save_rate: int = Field(..., ge=0, le=100, description="저축률")
    has_car: bool = Field(..., description="자동차 보유")
    monthly_rent: bool = Field(..., description="웰세 여부")

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "unique_id": "2323f2ac-4066-4e32-9412-0321c70dd8dc",
                "age": 30,
                "save_rate": 50,
                "has_car": False,
                "monthly_rent": True,
            }
        },
    )


class UserCarRankResponse(BaseModel):
    car: str = Field(..., description="자동차 등급")
    percentage: int = Field(..., description="비교 등급")

    model_config = ConfigDict(
        json_schema_extra={"example": {"car": "benz", "percentage": 25}},
    )
