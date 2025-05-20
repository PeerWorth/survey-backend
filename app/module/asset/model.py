from __future__ import annotations

import uuid

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.mixin.timestamp import TimestampMixin
from app.module.auth.model import User, UserConsent  # noqa: F401
from database.config import MySQLBase


class JobGroup(TimestampMixin, MySQLBase):
    __tablename__ = "job_group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    jobs: Mapped[list[Job]] = relationship("Job", back_populates="group")


class Job(TimestampMixin, MySQLBase):
    __tablename__ = "job"
    __table_args__ = (UniqueConstraint("group_id", "name", name="uniq_job_group_job_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("job_group.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    group: Mapped[JobGroup] = relationship("JobGroup", back_populates="jobs")
    salary: Mapped[list[UserSalary]] = relationship("UserSalary", back_populates="job")
    stats: Mapped[list[SalaryStat]] = relationship("SalaryStat", back_populates="job")


class SalaryStat(TimestampMixin, MySQLBase):
    __tablename__ = "salary_stat"
    __table_args__ = (UniqueConstraint("job_id", "experience", name="uniq_stat_combo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("job.id"), nullable=True, index=True)
    experience: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="경력")

    lower: Mapped[int] = mapped_column(Integer, nullable=False)
    avg: Mapped[int] = mapped_column(Integer, nullable=False)
    upper: Mapped[int] = mapped_column(Integer, nullable=False)

    job: Mapped[Job] = relationship("Job", back_populates="stats")


class UserSalary(TimestampMixin, MySQLBase):
    __tablename__ = "user_salary"

    id: Mapped[bytes] = mapped_column(
        BINARY(16),
        primary_key=True,
        default=lambda: uuid.uuid4().bytes,
        unique=True,
        nullable=False,
    )
    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=True,
    )
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("job.id"), nullable=False)
    experience: Mapped[int] = mapped_column(Integer, nullable=False, comment="경력")
    salary: Mapped[int] = mapped_column(Integer, nullable=False, comment="연봉")

    user: Mapped[User] = relationship("User", back_populates="salary")
    job: Mapped[Job] = relationship("Job", back_populates="salary")
    profile: Mapped[UserProfile] = relationship("UserProfile", back_populates="salary", uselist=False)


class UserProfile(TimestampMixin, MySQLBase):
    __tablename__ = "user_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    salary_id: Mapped[bytes] = mapped_column(
        BINARY(16),
        ForeignKey("user_salary.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    age: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="나이")
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True, comment="성별")
    save_rate: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="저축률")
    has_car: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment="자동차 보유")

    salary: Mapped[UserSalary] = relationship("UserSalary", back_populates="profile")
