from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.common.mixin.timestamp import TimestampMixin
from database.config import MySQLBase


class User(TimestampMixin, MySQLBase):
    __tablename__ = "user"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)

    consent = relationship("UserConsent", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    salary = relationship(
        "UserSalary",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class UserConsent(TimestampMixin, MySQLBase):
    __tablename__ = "user_consent"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    event = Column(String(255), nullable=False)
    agree = Column(Boolean, nullable=False)

    user = relationship("User", back_populates="consent")
