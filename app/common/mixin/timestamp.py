from sqlalchemy import Boolean, Column, DateTime

from app.common.utils.time import current_time_kst


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=current_time_kst, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=current_time_kst,
        onupdate=current_time_kst,
        nullable=False,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
