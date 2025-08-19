import importlib
import os


def get_config():
    """환경변수를 기반으로 적절한 config를 반환합니다."""
    env = os.environ.get("ENVIRONMENT", "dev").lower()

    if env not in ["dev", "prod"]:
        raise ValueError(f"지원하지 않는 환경입니다: {env}")

    config_module = importlib.import_module(f"config.{env}")
    return config_module
