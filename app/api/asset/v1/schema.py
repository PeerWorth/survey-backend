from pydantic import BaseModel, Field

from app.module.asset.enum import Gender


class BaseReponse(BaseModel):
    status_code: int = Field(..., description="상태 코드")
    detail: str = Field(..., description="메시지")


class SubmissionPostRequest(BaseModel):
    job_id: int = Field(..., description="직무")
    experience: int = Field(..., ge=0, description="경력")
    salary: int = Field(..., gt=0, description="연봉")
    save_rate: int = Field(..., ge=0, le=100, description="저축률")
    age: int | None = Field(None, ge=20, le=70, description="나이")
    gender: Gender | None = Field(None, description="성별")

    class Config:
        use_enum_values = True
