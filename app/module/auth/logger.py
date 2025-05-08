from app.common.logger.config import create_logger
from main_config import settings

env_enum = settings.environment
cloudwatch_group = f"olass-{env_enum.value}-auth-errors"

auth_logger = create_logger(name=__name__, level=env_enum.log_level, cloudwatch_group=cloudwatch_group)
