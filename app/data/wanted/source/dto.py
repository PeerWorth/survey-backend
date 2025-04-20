from pydantic import BaseModel


class TooltipData(BaseModel):
    experience: int
    salary: int


class JobData(BaseModel):
    job_group: str
    job: str
    tooltip_data: list[TooltipData]
