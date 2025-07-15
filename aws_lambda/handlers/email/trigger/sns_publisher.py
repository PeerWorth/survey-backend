import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SnsPublisher:
    def __init__(self, sns_client, topic_arn: str):
        self.sns = sns_client
        self.topic_arn = topic_arn

    def publish_email_batch(self, email_type: str, email_batch: list[tuple[int, str]]):
        message = {
            "email_type": email_type,
            "emails": email_batch,
        }

        try:
            response = self.sns.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(message),
                MessageAttributes={
                    "email_type": {
                        "DataType": "String",
                        "StringValue": email_type,
                    }
                },
            )
            return response
        except Exception as e:
            logger.exception(f"SNS publish에 실패하였습니다. {e}")
            raise
