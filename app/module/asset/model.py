from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.common.mixin.timestamp import TimestampMixin
from database.config import MySQLBase


class JobGroup(TimestampMixin, MySQLBase):
    __tablename__ = "job_group"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)

    jobs = relationship("Job", back_populates="group")


class Job(TimestampMixin, MySQLBase):
    __tablename__ = "job"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("job_group.id"), nullable=False)
    name = Column(String(100), nullable=False)

    group = relationship("JobGroup", back_populates="jobs")
    submissions = relationship("SalarySubmission", back_populates="job")
    stats = relationship("SalaryStats", back_populates="job")


class SalarySubmission(TimestampMixin, MySQLBase):
    __tablename__ = "salary_submission"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("job.id"), nullable=False)
    years_experience = Column(Integer, nullable=False)
    salary = Column(Integer, nullable=False)

    job = relationship("Job", back_populates="submissions")


class SalaryStats(TimestampMixin, MySQLBase):
    __tablename__ = "salary_stats"
    __table_args__ = (UniqueConstraint("job_id", "years_experience", name="uniq_job_years"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("job.id"), nullable=False)
    years_experience = Column(Integer, nullable=False)
    avg_salary = Column(Integer, nullable=False)
    lower_25 = Column(Integer, nullable=False)
    upper_25 = Column(Integer, nullable=False)
    record_count = Column(Integer, nullable=False)

    job = relationship("Job", back_populates="stats")
