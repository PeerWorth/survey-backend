import json


class SnsPublisher:
    def __init__(self, sns_client, topic_arn: str):
        self.sns = sns_client
        self.topic_arn = topic_arn

    def publish_email_batch(self, email_type: str, email_batch: list[tuple[int, str]]):
        message = {
            "email_type": email_type,
            "emails": email_batch,
        }

        return self.sns.publish(
            TopicArn=self.topic_arn,
            Message=json.dumps(message),
            MessageAttributes={
                "email_type": {
                    "DataType": "String",
                    "StringValue": email_type,
                }
            },
        )
