from pydantic import BaseModel, Field


class BaseReponse(BaseModel):
    status_code: int = Field(..., description="상태 코드")
    detail: str = Field(..., description="메시지")
