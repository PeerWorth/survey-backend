from typing import Any

from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.common.schemas.base_schema import BaseResponseModel, to_camel


def convert_keys(obj: Any) -> Any:
    if isinstance(obj, BaseResponseModel):
        return obj.model_dump(by_alias=True)
    elif isinstance(obj, BaseModel):
        return obj.model_dump(by_alias=True)
    elif isinstance(obj, dict):
        return {to_camel(k) if isinstance(k, str) else k: convert_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_keys(i) for i in obj]
    return obj


class CustomJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return super().render(convert_keys(content))
