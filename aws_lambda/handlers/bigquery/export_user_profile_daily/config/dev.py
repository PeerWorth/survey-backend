import os

BIGQUERY_PROJECT = "olass-dev"
BIGQUERY_USER_TABLE = f"{BIGQUERY_PROJECT}.datamart.user_profile_daily"
BIGQUERY_JOURNEY_TABLE = f"{BIGQUERY_PROJECT}.datamart.user_journey_daily"

GA4_PROPERTY_ID = os.environ.get("DEV_GA4_PROPERTY_ID")
if not GA4_PROPERTY_ID:
    raise ValueError("DEV_GA4_PROPERTY_ID 환경변수가 설정되지 않았습니다.")

BIGQUERY_ANALYTICS_DATASET = f"{BIGQUERY_PROJECT}.analytics_{GA4_PROPERTY_ID}"
MAX_ROWS_PER_REQUEST = 5000  # 공식 제한은 10,000이지만 절반으로 안전하게 수행

CREDENTIALS_ENV_VAR = "DEV_BIGQUERY_CREDENTIALS_JSON"
