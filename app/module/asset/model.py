from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from app.common.mixin.timestamp import TimestampMixin

if TYPE_CHECKING:
    from app.module.auth.model import User


class JobGroup(TimestampMixin, table=True):
    __tablename__: str = "job_group"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(sa_column_kwargs={"nullable": False, "unique": True})

    jobs: list[Job] = Relationship(back_populates="group")


class Job(TimestampMixin, table=True):
    __tablename__: str = "job"
    __table_args__ = (UniqueConstraint("group_id", "name", name="uniq_job_group_job_name"),)

    id: int | None = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="job_group.id", nullable=False)
    name: str
    name_en: str | None = None

    group: JobGroup | None = Relationship(back_populates="jobs")
    salary: list[UserSalary] = Relationship(back_populates="job")
    stats: list[SalaryStat] = Relationship(back_populates="job")


class SalaryStat(TimestampMixin, table=True):
    __tablename__: str = "salary_stat"
    __table_args__ = (UniqueConstraint("job_id", "experience", name="uniq_stat_combo"),)

    id: int | None = Field(default=None, primary_key=True)
    job_id: int | None = Field(foreign_key="job.id", nullable=True, index=True)
    experience: int | None = Field(default=None, description="경력")
    avg: int = Field(description="평균 연봉")

    job: Job | None = Relationship(back_populates="stats")


class UserSalary(TimestampMixin, table=True):
    __tablename__: str = "user_salary"

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: int | None = Field(foreign_key="user.id", nullable=True)
    job_id: int = Field(foreign_key="job.id")
    experience: int = Field(description="경력")
    salary: int = Field(description="연봉")

    user: User | None = Relationship(back_populates="salary")
    job: Job | None = Relationship(back_populates="salary")
    profile: UserProfile | None = Relationship(back_populates="salary")


class UserProfile(TimestampMixin, table=True):
    __tablename__: str = "user_profile"

    id: int | None = Field(default=None, primary_key=True)
    salary_id: UUID = Field(foreign_key="user_salary.id", nullable=False, unique=True)
    age: int | None = Field(nullable=True, description="나이")
    gender: str | None = Field(nullable=True, description="성별")
    save_rate: int | None = Field(nullable=True, description="저축률")
    has_car: bool | None = Field(nullable=True, description="자동차 보유")

    salary: UserSalary | None = Relationship(back_populates="profile")
