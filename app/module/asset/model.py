from typing import Optional
from uuid import uuid4

from sqlalchemy import BINARY, Column, ForeignKey, UniqueConstraint
from sqlmodel import Field, Relationship

from app.common.mixin.timestamp import TimestampMixin


class JobGroup(TimestampMixin, table=True):
    __tablename__: str = "job_group"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(sa_column_kwargs={"nullable": False, "unique": True})

    jobs: list["Job"] = Relationship(back_populates="group")


class Job(TimestampMixin, table=True):
    __tablename__: str = "job"
    __table_args__ = (UniqueConstraint("group_id", "name", name="uniq_job_group_job_name"),)

    id: int = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="job_group.id", nullable=False)
    name: str

    group: JobGroup | None = Relationship(back_populates="jobs")
    salary: list["UserSalary"] = Relationship(back_populates="job")
    stats: list["SalaryStat"] = Relationship(back_populates="job")


class SalaryStat(TimestampMixin, table=True):
    __tablename__: str = "salary_stat"
    __table_args__ = (UniqueConstraint("job_id", "experience", name="uniq_stat_combo"),)

    id: int = Field(default=None, primary_key=True)
    job_id: int | None = Field(foreign_key="job.id", nullable=True, index=True)
    experience: int | None = Field(default=None, description="경력")
    avg: int = Field(description="평균 연봉")

    job: Job | None = Relationship(back_populates="stats")


class UserSalary(TimestampMixin, table=True):
    __tablename__: str = "user_salary"

    id: bytes = Field(
        default_factory=uuid4,
        sa_column=Column("id", BINARY(16), primary_key=True),
    )
    user_id: int | None = Field(foreign_key="user.id", nullable=True)
    job_id: int = Field(foreign_key="job.id")
    experience: int = Field(description="경력")
    salary: int = Field(description="연봉")

    job: Job | None = Relationship(back_populates="salary")
    profile: Optional["UserProfile"] = Relationship(back_populates="salary")


class UserProfile(TimestampMixin, table=True):
    __tablename__: str = "user_profile"

    id: int = Field(default=None, primary_key=True)
    salary_id: bytes = Field(
        sa_column=Column(
            "salary_id",
            BINARY(16),
            ForeignKey("user_salary.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
            comment="user_salary.id (16-byte UUID)",
        )
    )
    age: int | None = Field(nullable=True, description="나이")
    save_rate: int | None = Field(nullable=True, description="저축률")
    has_car: bool | None = Field(nullable=True, description="자동차 보유")
    is_monthly_rent: bool | None = Field(nullable=True, description="월세 여부")

    salary: UserSalary | None = Relationship(back_populates="profile")
