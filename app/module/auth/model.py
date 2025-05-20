from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.mixin.timestamp import TimestampMixin
from app.module.asset.model import UserSalary
from database.config import MySQLBase


class User(TimestampMixin, MySQLBase):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    consent: Mapped[list[UserConsent]] = relationship(
        "UserConsent",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    salary: Mapped[list[UserSalary]] = relationship(
        "UserSalary",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class UserConsent(TimestampMixin, MySQLBase):
    __tablename__ = "user_consent"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    event: Mapped[str] = mapped_column(String(255), nullable=False)
    agree: Mapped[bool] = mapped_column(Boolean, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="consent")
