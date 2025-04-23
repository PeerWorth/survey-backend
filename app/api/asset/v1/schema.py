from typing import Self  # type: ignore[attr-defined]

from pydantic import BaseModel, Field

from app.module.asset.enum import Gender


class BaseReponse(BaseModel):
    status_code: int = Field(..., description="상태 코드")
    detail: str = Field(..., description="메시지")


class SubmissionPostRequest(BaseModel):
    job: str = Field(..., description="직무")
    experience: int = Field(..., description="경력")
    salary: int = Field(..., description="연봉")
    save_rate: int = Field(..., description="저축률")
    age: int | None = Field(None, description="나이")
    gender: Gender | None = Field(None, description="성별")

    class Config:
        use_enum_values = True

    @classmethod
    def validate(cls, request_data: Self):

        # TODO: 요청 body값 검증 필요
        pass
