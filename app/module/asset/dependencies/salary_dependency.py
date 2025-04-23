from app.module.asset.services.salary_service import SalaryService

salary_service = SalaryService()


def get_salary_service() -> SalaryService:
    return salary_service
