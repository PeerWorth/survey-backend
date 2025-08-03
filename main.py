from app.common.config.app_config import AppFactory

app = AppFactory.create_factory().create_app()
