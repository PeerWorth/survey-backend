from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class BaseRequestModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class BaseResponseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    def model_dump(self, **kwargs):
        """기본 응답은 camelCase로 직렬화되도록 보장"""
        return super().model_dump(by_alias=True, **kwargs)


class SuccessResponse(BaseResponseModel):
    code: int = Field(default=..., examples=[200])
    data: Any = Field(default={})
    message: str = Field(default="요청이 성공적으로 처리되었습니다.")
    success: bool = Field(default=True)


class ErrorDetail(BaseResponseModel):
    type: str = Field(default=..., description="에러 타입", examples=["ValidationError"])
    details: dict[str, Any] | None = Field(
        default=None, description="에러 상세 필드별 메시지", examples=[{"email": "이메일 형식이 잘못되었습니다."}]
    )


class ErrorResponse(BaseResponseModel):
    code: int = Field(default=..., description="HTTP 상태 코드", examples=[403])
    message: str = Field(default=..., description="에러 메시지", examples=["유효하지 않은 요청입니다."])
    error: ErrorDetail
    success: bool = Field(default=False, description="성공 여부", examples=[False])
