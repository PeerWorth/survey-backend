import asyncio
import logging

from service import UserService

logger = logging.getLogger(__name__)
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


async def _lambda_handler(event: dict, context):
    logger.info("Bigquery로 유저 정보를 보내기 시작합니다.")
    service = await UserService.create()
    user_profiles: list[dict] = await service.get_user_profiles()

    logger.info(f"총 {len(user_profiles)}개의 행이 BigQuery로 전송합니다.")

    if not user_profiles:
        logger.info("전송할 데이터가 없습니다.")
        return

    try:
        await service.insert_to_bigquery(user_profiles)
    except Exception as e:
        logger.exception("BigQuery 전송 중 오류 발생", exc_info=e)
