from pydantic import UUID4, BaseModel, Field


class UserEmailRequest(BaseModel):
    unique_id: UUID4 = Field(..., description="클라이언트 uuid")
    email: str = Field(..., description="이메일")
    agree: bool = Field(..., description="이메일 수신 동의")
