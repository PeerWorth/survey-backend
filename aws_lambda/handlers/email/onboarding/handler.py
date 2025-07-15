import json
import logging

from service import send_onboarding_email

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# BatchSize를 1로 설정한 상태를 전제하였습니다.
def lambda_handler(event: dict, context):
    record = event["Records"][0]
    message_id = record.get("messageId", "unknown")
    logger.info(f"메시지 id: {message_id}를 전달 받았습니다.")

    try:
        body = json.loads(record["body"])
        emails = body.get("emails", [])

        if not emails:
            logger.warning(f"메시지 id: {message_id}에서 이메일 리스트가 없습니다")
            raise ValueError("이메일이 안왔습니다.")

        logger.info(f"총 {len(emails)}명의 유저에게 이메일 전송을 시도합니다.")
        result = send_onboarding_email(emails)

        return {"status": "ok", "result": result}

    except Exception as e:
        logger.exception(f"onboarding 메일 전송 중 에러 발생하였습니다.: {message_id} - {str(e)}")
        raise
