from app.module.asset.services.asset_service import AssetService

salary_service = AssetService()


def get_salary_service() -> AssetService:
    return salary_service
