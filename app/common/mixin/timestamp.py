from datetime import datetime

from sqlmodel import Field, SQLModel

from app.common.utils.time import current_time_kst


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=current_time_kst, nullable=False)
    updated_at: datetime = Field(default_factory=current_time_kst, nullable=False)
    deleted_at: datetime | None = Field(default=None)
    is_deleted: bool = Field(default=False)
