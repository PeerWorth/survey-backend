import asyncio
import logging

from service import UserJourneyService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        return loop.create_task(_lambda_handler(event, context))
    else:
        return loop.run_until_complete(_lambda_handler(event, context))


async def _lambda_handler(event, context):
    try:
        total_send = UserJourneyService.run_etl_pipeline()

        logger.info(f"ETL 파이프라인 완료 - 처리된 이벤트: {total_send}개")

        return

    except Exception as e:
        logger.error(f"ETL 파이프라인 오류 발생: {e}")
        return
