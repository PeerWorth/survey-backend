from pydantic import UUID4, ConfigDict, Field

from app.common.schemas.base_schema import BaseRequestModel


class UserEmailRequest(BaseRequestModel):
    unique_id: UUID4 = Field(..., description="클라이언트 uuid")
    email: str = Field(..., description="이메일")
    agree: bool = Field(..., description="이메일 수신 동의")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {"unique_id": "2323f2ac-4066-4e32-9412-0321c70dd8dc", "email": "olass.@gmail.com", "agree": True}
        },
    )
