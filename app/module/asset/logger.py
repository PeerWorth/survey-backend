from app.common.enums import EnvironmentType
from app.common.logger.config import create_logger
from main_config import settings

env_enum: EnvironmentType = settings.environment
cloudwatch_group = f"olass-{env_enum.log_env}-asset"

asset_logger = create_logger(name=__name__, level=env_enum.log_level, cloudwatch_group=cloudwatch_group)
