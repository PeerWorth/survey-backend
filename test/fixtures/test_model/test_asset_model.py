from dataclasses import dataclass

from app.module.asset.model import Job, JobGroup, SalaryStat, UserProfile, UserSalary


@dataclass
class AssetTestData:
    job_group: JobGroup
    job: Job
    salary_stat: SalaryStat
    user_salary: UserSalary
    user_profile: UserProfile
