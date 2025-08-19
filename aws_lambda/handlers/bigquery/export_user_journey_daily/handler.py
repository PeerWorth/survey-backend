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
        service = UserJourneyService()

        events = service.process_user_journey_data()

        if not events:
            logger.info("오늘 날짜의 이벤트가 존재하지 않습니다.")
            return

        logger.info(f"총 {len(events)}개의 GA4 이벤트를 처리하였습니다.")

        return

    except Exception as e:
        logger.error(f"오류 발생: {e}")
        return
