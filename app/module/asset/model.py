from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.common.mixin.timestamp import TimestampMixin
from database.config import MySQLBase


class JobGroup(TimestampMixin, MySQLBase):
    __tablename__ = "job_group"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)

    jobs = relationship("Job", back_populates="group")


class Job(TimestampMixin, MySQLBase):
    __tablename__ = "job"
    __table_args__ = (UniqueConstraint("group_id", "name", name="uniq_job_group_job_name"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("job_group.id"), nullable=False)
    name = Column(String(100), nullable=False)

    group = relationship("JobGroup", back_populates="jobs")
    submissions = relationship("SalarySubmission", back_populates="job")
    stats = relationship("SalaryStat", back_populates="job")


class SalarySubmission(TimestampMixin, MySQLBase):
    __tablename__ = "salary_submission"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("job.id"), nullable=False)
    experience = Column(Integer, nullable=False, comment="경력")
    salary = Column(Integer, nullable=False, comment="연봉")
    save_rate = Column(Integer, nullable=False, comment="저축률")
    age = Column(Integer, nullable=True, comment="나이")
    gender = Column(String(10), nullable=True, comment="성별")

    job = relationship("Job", back_populates="submissions")


class SalaryStat(TimestampMixin, MySQLBase):
    __tablename__ = "salary_stat"
    __table_args__ = (UniqueConstraint("job_id", "experience", "age_group", name="uniq_stat_combo"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("job.id"), nullable=True, index=True)
    experience = Column(Integer, nullable=True, comment="경력")

    age_group = Column(Integer, nullable=True, comment="나이대")

    lower = Column(Integer, nullable=False)
    avg = Column(Integer, nullable=False)
    upper = Column(Integer, nullable=False)

    job = relationship("Job", back_populates="stats")
