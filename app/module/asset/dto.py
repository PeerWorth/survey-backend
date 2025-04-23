from pydantic import BaseModel, Field

from app.module.asset.enum import Gender


class SalarySubmissionData(BaseModel):
    job: str = Field(..., description="직무")
    experience: int = Field(..., description="경력")
    salary: int = Field(..., description="연봉")
    save_rate: int = Field(..., description="저축률")
    age: int | None = Field(None, description="나이")
    gender: Gender | None = Field(None, description="성별")

    class Config:
        use_enum_values = True
