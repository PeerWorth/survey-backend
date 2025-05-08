import logging
from logging import Logger

import boto3
import watchtower
from botocore.exceptions import NoCredentialsError
from mypy_boto3_logs.client import CloudWatchLogsClient


def create_logger(
    name: str,
    level: str = "INFO",
    cloudwatch_group: str | None = None,
    retention_days: int = 14,
) -> Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(ch)

    if cloudwatch_group:
        try:
            session = boto3.Session(region_name="ap-northeast-2")

            cw_client = session.client("logs")

            cw = watchtower.CloudWatchLogHandler(
                boto3_client=cw_client,
                log_group=cloudwatch_group,
                create_log_group=True,
                stream_name="{strftime:%Y-%m-%d}/{process_id}",
                send_interval=5,
            )
            cw.setLevel(level)
            logger.addHandler(cw)

            logs_client: CloudWatchLogsClient = boto3.client("logs", region_name="ap-northeast-2")
            logs_client.put_retention_policy(logGroupName=cloudwatch_group, retentionInDays=retention_days)

        except NoCredentialsError:
            logger.warning("AWS 자격 증명 없어서 CloudWatch 로그 미적용")
        except Exception as e:
            logger.warning(f"CloudWatch retention 설정 실패: {e}")

    return logger
