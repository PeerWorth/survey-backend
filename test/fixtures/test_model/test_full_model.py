from dataclasses import dataclass

from app.module.asset.model import Job, JobGroup, SalaryStat, UserProfile, UserSalary
from app.module.auth.model import User, UserConsent


@dataclass
class FullTestData:
    job_group: JobGroup
    job: Job
    salary_stat: SalaryStat
    user_salary: UserSalary
    user_profile: UserProfile
    user: User
    user_consent: UserConsent
