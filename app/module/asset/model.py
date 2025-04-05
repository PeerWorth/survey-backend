from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.mixin.timestamp import TimestampMixin
from database.config import MySQLBase


class Asset(TimestampMixin, MySQLBase):
    __tablename__ = "asset"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    asset_type: Mapped[str] = mapped_column(String(255), nullable=False, info={"description": "자산 종류"})
