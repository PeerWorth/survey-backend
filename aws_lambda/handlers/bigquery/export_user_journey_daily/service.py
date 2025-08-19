import json
import logging
import os
from datetime import datetime, timedelta

from config import get_config
from google.cloud import bigquery
from google.oauth2 import service_account

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class UserJourneyService:
    EVENTS_QUERY = """
    SELECT
        event_date,
        user_pseudo_id,
        event_name,
        COUNT(*) as event_count
    FROM `{dataset}.events_{date}`
    WHERE user_pseudo_id IS NOT NULL
        AND event_name IN (
            'click_olass_intro',
            'click_salary_comparison_job',
            'click_salary_comparison_salary',
            'click_salary_comparison_experience',
            'click_salary_comparison_result',
            'click_asset_test_question_age',
            'click_asset_test_question_invest_ratio',
            'click_asset_test_question_own_car',
            'click_asset_test_question_monthly_rent',
            'click_agree_terms',
            'click_share_button'
        )
    GROUP BY event_date, user_pseudo_id, event_name
    LIMIT 1000
    """

    UTM_QUERY = """
    SELECT
        user_pseudo_id,
        traffic_source.source as utm_source,
        traffic_source.medium as utm_medium,
        traffic_source.name as utm_campaign,
        (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'utm_content') as utm_content,
        (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'utm_term') as utm_term
    FROM `{dataset}.events_{date}`
    WHERE user_pseudo_id IS NOT NULL
        AND traffic_source.source IS NOT NULL
    QUALIFY ROW_NUMBER() OVER (PARTITION BY user_pseudo_id ORDER BY event_timestamp ASC) = 1
    """

    def __init__(self):
        self.config = get_config()
        self.client = self._get_bigquery_client()

    def _get_bigquery_client(self):
        credentials = self._get_credentials()
        return bigquery.Client(credentials=credentials)

    def _get_credentials(self):
        gcp_key_json = os.environ.get(self.config.CREDENTIALS_ENV_VAR)
        if gcp_key_json:
            try:
                key_data = json.loads(gcp_key_json)
                return service_account.Credentials.from_service_account_info(key_data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing 변환 중 에러: {e}")
                raise

        return None

    def get_ga4_events_yesterday(self):
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

        query = self.EVENTS_QUERY.format(dataset=self.config.BIGQUERY_ANALYTICS_DATASET, date=yesterday)

        try:
            events_job = self.client.query(query)
            events_results = events_job.result()

            events = []
            for row in events_results:
                events.append(
                    {
                        "event_date": str(row.event_date),
                        "user_pseudo_id": row.user_pseudo_id,
                        "event_name": row.event_name,
                        "event_count": row.event_count,
                    }
                )

            logger.info(f"이벤트 데이터 {len(events)}개 조회 완료")
            return events

        except Exception as e:
            logger.error(f"GA4 이벤트 로그를 가져오는 중 에러 발생: {e}")
            raise

    def get_utm_data_yesterday(self):
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

        query = self.UTM_QUERY.format(dataset=self.config.BIGQUERY_ANALYTICS_DATASET, date=yesterday)

        try:
            utm_job = self.client.query(query)
            utm_results = utm_job.result()

            utm_data = {}
            for row in utm_results:
                utm_data[row.user_pseudo_id] = {
                    "utm_source": row.utm_source,
                    "utm_medium": row.utm_medium,
                    "utm_campaign": row.utm_campaign,
                    "utm_content": row.utm_content,
                    "utm_term": row.utm_term,
                }

            logger.info(f"UTM 데이터 {len(utm_data)}개 사용자 조회 완료")
            return utm_data

        except Exception as e:
            logger.error(f"UTM 데이터 조회 중 에러 발생: {e}")
            raise

    def process_user_journey_data(self):
        events = self.get_ga4_events_yesterday()
        utm_data = self.get_utm_data_yesterday()

        enriched_events = []
        for event in events:
            user_id = event["user_pseudo_id"]
            utm_info = utm_data.get(user_id, {})

            enriched_event = {
                **event,
                "utm_source": utm_info.get("utm_source"),
                "utm_medium": utm_info.get("utm_medium"),
                "utm_campaign": utm_info.get("utm_campaign"),
                "utm_content": utm_info.get("utm_content"),
                "utm_term": utm_info.get("utm_term"),
            }
            enriched_events.append(enriched_event)

        logger.info(f"총 {len(enriched_events)}개 이벤트 처리 완료")
        return enriched_events
