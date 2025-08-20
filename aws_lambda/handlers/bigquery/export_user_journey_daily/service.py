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
        COUNTIF(event_name = 'click_olass_intro') as intro_page,
        COUNTIF(event_name = 'click_salary_comparison_job') as salary_job,
        COUNTIF(event_name = 'click_salary_comparison_salary') as salary_salary,
        COUNTIF(event_name = 'click_salary_comparison_experience') as salary_experience,
        COUNTIF(event_name = 'click_asset_test_question_age') as profile_age,
        COUNTIF(event_name = 'click_asset_test_question_invest_ratio') as profile_invest_ratio,
        COUNTIF(event_name = 'click_asset_test_question_own_car') as profile_car,
        COUNTIF(event_name = 'click_asset_test_question_monthly_rent') as profile_rent,
        COUNTIF(event_name = 'click_agree_terms') as terms_agreed,
        COUNTIF(event_name = 'click_share_result') as share_button
    FROM `{dataset}.events_{date}`
    WHERE user_pseudo_id IS NOT NULL
        AND event_name IN (
            'click_olass_intro',
            'click_salary_comparison_job',
            'click_salary_comparison_salary',
            'click_salary_comparison_experience',
            'click_asset_test_question_age',
            'click_asset_test_question_invest_ratio',
            'click_asset_test_question_own_car',
            'click_asset_test_question_monthly_rent',
            'click_agree_terms',
            'click_share_result'
        )
    GROUP BY event_date, user_pseudo_id
    """

    UTM_QUERY = """
    SELECT
        user_pseudo_id,
        collected_traffic_source.manual_source as utm_source,
        collected_traffic_source.manual_medium as utm_medium,
        collected_traffic_source.manual_campaign_name as utm_campaign,
        collected_traffic_source.manual_content as utm_content,
        collected_traffic_source.manual_term as utm_term
    FROM `{dataset}.events_{date}`
    WHERE user_pseudo_id IS NOT NULL
        AND collected_traffic_source.manual_source IS NOT NULL
    QUALIFY ROW_NUMBER() OVER (PARTITION BY user_pseudo_id ORDER BY event_timestamp ASC) = 1
    """

    @staticmethod
    def _get_bigquery_client():
        credentials = UserJourneyService._get_credentials()
        return bigquery.Client(credentials=credentials)

    @staticmethod
    def _get_credentials():
        config = get_config()
        gcp_key_json = os.environ.get(config.CREDENTIALS_ENV_VAR)
        if gcp_key_json:
            try:
                key_data = json.loads(gcp_key_json)
                return service_account.Credentials.from_service_account_info(key_data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing 변환 중 에러: {e}")
                raise

        return None

    @staticmethod
    def get_ga4_events_yesterday(client, config):
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

        query = UserJourneyService.EVENTS_QUERY.format(dataset=config.BIGQUERY_ANALYTICS_DATASET, date=yesterday)

        try:
            events_job = client.query(query)
            events_results = events_job.result()

            events = []
            for row in events_results:
                event_date_str = str(row.event_date)
                date_obj = datetime.strptime(event_date_str, "%Y%m%d")
                formatted_date = date_obj.strftime("%Y-%m-%d")

                events.append(
                    {
                        "event_date": formatted_date,
                        "user_pseudo_id": row.user_pseudo_id,
                        "intro_page": row.intro_page,
                        "salary_job": row.salary_job,
                        "salary_salary": row.salary_salary,
                        "salary_experience": row.salary_experience,
                        "profile_age": row.profile_age,
                        "profile_invest_ratio": row.profile_invest_ratio,
                        "profile_car": row.profile_car,
                        "profile_rent": row.profile_rent,
                        "terms_agreed": row.terms_agreed,
                        "share_button": row.share_button,
                    }
                )

            logger.info(f"이벤트 데이터 {len(events)}개 조회 완료")
            return events

        except Exception as e:
            logger.error(f"GA4 이벤트 로그를 가져오는 중 에러 발생: {e}")
            raise

    @staticmethod
    def get_utm_data_yesterday(client, config):
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

        query = UserJourneyService.UTM_QUERY.format(dataset=config.BIGQUERY_ANALYTICS_DATASET, date=yesterday)

        try:
            utm_job = client.query(query)
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

    @staticmethod
    def process_user_journey_data(client, config):
        events = UserJourneyService.get_ga4_events_yesterday(client, config)
        utm_data = UserJourneyService.get_utm_data_yesterday(client, config)

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

    @staticmethod
    def insert_to_bigquery(client, config, enriched_events):
        table_id = f"{config.BIGQUERY_PROJECT_ID}.{config.BIGQUERY_DATAMART_DATASET}.user_journey_daily"

        try:
            rows_to_insert = []
            for event in enriched_events:
                row = {
                    "event_date": event["event_date"],
                    "user_pseudo_id": event["user_pseudo_id"],
                    "intro_page": event["intro_page"],
                    "salary_job": event["salary_job"],
                    "salary_salary": event["salary_salary"],
                    "salary_experience": event["salary_experience"],
                    "profile_age": event["profile_age"],
                    "profile_invest_ratio": event["profile_invest_ratio"],
                    "profile_car": event["profile_car"],
                    "profile_rent": event["profile_rent"],
                    "terms_agreed": event["terms_agreed"],
                    "share_button": event["share_button"],
                    "utm_source": event["utm_source"],
                    "utm_medium": event["utm_medium"],
                    "utm_campaign": event["utm_campaign"],
                    "utm_content": event["utm_content"],
                    "utm_term": event["utm_term"],
                }
                rows_to_insert.append(row)

            table = client.get_table(table_id)
            errors = client.insert_rows_json(table, rows_to_insert)

            if errors:
                logger.error(f"BigQuery 삽입 중 에러 발생: {errors}")
                raise Exception(f"BigQuery insertion failed: {errors}")

            logger.info(f"BigQuery에 {len(rows_to_insert)}개 행 삽입 완료")

        except Exception as e:
            logger.error(f"BigQuery 테이블 삽입 중 에러 발생: {e}")
            raise

    @staticmethod
    def run_etl_pipeline() -> int:
        logger.info("GA4 to BigQuery ETL 파이프라인 시작")

        config = get_config()
        client = UserJourneyService._get_bigquery_client()

        enriched_events = UserJourneyService.process_user_journey_data(client, config)
        if not enriched_events:
            logger.info("처리할 데이터가 없습니다")
            return 0

        UserJourneyService.insert_to_bigquery(client, config, enriched_events)

        logger.info("ETL 파이프라인 완료")
        return len(enriched_events)
