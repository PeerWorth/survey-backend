from pydantic import BaseModel, Field


class BaseReponse(BaseModel):
    status_code: int = Field(..., description="상태 코드")
    detail: str = Field(..., description="메시지")


class UserSalaryPostRequest(BaseModel):
    job_id: int = Field(..., description="직무")
    experience: int = Field(..., ge=0, description="경력")
    salary: int = Field(..., gt=0, description="연봉")

    class Config:
        use_enum_values = True


class JobsGetResponse(BaseModel):
    job_id: int = Field(..., description="직무 id, 추후 POST 요청 시 선택한 직무 id 반환")
    name: str = Field(..., description="직무명")
