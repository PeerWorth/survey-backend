import logging
from logging import Logger

import watchtower
from botocore.exceptions import NoCredentialsError


def create_logger(name: str, level: str = "INFO", cloudwatch_group: str | None = None) -> Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # 중복 생성 방지

    logger.setLevel(level)

    # 1) 콘솔 핸들러
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(ch)

    if cloudwatch_group:
        try:
            cw = watchtower.CloudWatchLogHandler(log_group=cloudwatch_group, create_log_group=True)
            logger.addHandler(cw)
        except NoCredentialsError:
            logger.warning("AWS 자격 증명 없어서 CloudWatch 로그 미적용")

    return logger
