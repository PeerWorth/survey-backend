import logging
from logging import Logger
from typing import cast

import boto3
import watchtower
from botocore.exceptions import NoCredentialsError
from mypy_boto3_logs.client import CloudWatchLogsClient

from app.common.logger.enums import LogTag


class TaggedLogger(logging.Logger):
    _LEVEL_TAG_MAP = {
        logging.DEBUG: LogTag.DEBUG.value,
        logging.INFO: LogTag.INFO.value,
        logging.WARNING: LogTag.WARN.value,
        logging.ERROR: LogTag.ERROR.value,
        logging.CRITICAL: LogTag.CRITICAL.value,
    }

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None):
        tag = None
        if extra and isinstance(extra, dict) and "tag" in extra:
            tag = extra["tag"]
        else:
            tag = self._LEVEL_TAG_MAP.get(level, LogTag.INFO.value)

        msg = f"[{tag}] {msg}"

        return super().makeRecord(name, level, fn, lno, msg, args, exc_info, func, extra, sinfo)


logging.setLoggerClass(TaggedLogger)


def create_logger(
    name: str,
    level: str = LogTag.INFO.value,
    cloudwatch_group: str | None = None,
    retention_days: int = 14,
) -> Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(ch)

    if cloudwatch_group:
        try:
            session = boto3.Session(region_name="ap-northeast-2")
            cw_client = session.client("logs")

            cw = watchtower.CloudWatchLogHandler(
                boto3_client=cw_client,
                log_group=cloudwatch_group,
                create_log_group=True,
                stream_name="{strftime:%Y-%m-%d}",
                send_interval=10,
            )
            cw.setLevel(level)
            cw.setFormatter(ch.formatter)
            logger.addHandler(cw)

            logs_client = cast(CloudWatchLogsClient, boto3.client("logs", region_name="ap-northeast-2"))
            logs_client.put_retention_policy(logGroupName=cloudwatch_group, retentionInDays=retention_days)
        except NoCredentialsError:
            logger.warning("AWS 자격 증명 없어서 CloudWatch 로그 미적용")
        except Exception as e:
            logger.warning(f"CloudWatch retention 설정 실패: {e}")

    return logger
