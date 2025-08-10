import json
import logging
import os

from constant import BIGQUERY_USER_TABLE, MAX_ROWS_PER_REQUEST
from google.cloud import bigquery
from google.oauth2 import service_account
from more_itertools import chunked
from repository import UserRepository
from shared.db_config import get_session

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class UserService:
    def __init__(self, repository: UserRepository, session):
        self.repository = repository
        self.session = session

    @classmethod
    async def create(cls):
        session = await get_session()
        repo = UserRepository(session)
        return cls(repository=repo, session=session)

    async def get_user_profiles(self) -> list[dict]:
        try:
            return await self.repository.get_user_profiles()
        finally:
            await self.session.close()

    def insert_to_bigquery(self, rows: list[dict]):
        credentials = self._get_credentials()
        client = bigquery.Client(credentials=credentials)

        event_date = rows[0]["event_date"]
        self._delete_existing_data(client, event_date)

        chunks = list(chunked(rows, MAX_ROWS_PER_REQUEST))
        total_success = 0

        for idx, chunk in enumerate(chunks):
            errors = client.insert_rows_json(BIGQUERY_USER_TABLE, chunk)
            if errors:
                logger.error(f"[Chunk {idx + 1}/{len(chunks)}] 일부 행 insert 실패: {errors}")
            else:
                logger.info(f"[Chunk {idx + 1}/{len(chunks)}] {len(chunk)}개 행 삽입 성공")
                total_success += len(chunk)

        logger.info(f"[BigQuery Insert 완료] 총 삽입 성공: {total_success} / 전체: {len(rows)}")

    def _get_credentials(self):
        gcp_key_json = os.environ.get("DEV_BIGQUERY_CREDENTIALS_JSON")
        if gcp_key_json:
            try:
                key_data = json.loads(gcp_key_json)
                return service_account.Credentials.from_service_account_info(key_data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 오류: {e}")
                raise

        logger.warning("Google Cloud 인증 정보가 설정되지 않았습니다. 기본 인증을 사용합니다.")
        return None

    def _delete_existing_data(self, client: bigquery.Client, event_date: str):
        delete_query = f"""
            DELETE FROM {BIGQUERY_USER_TABLE}
            WHERE event_date = '{event_date}'
        """

        try:
            query_job = client.query(delete_query)
            query_job.result()
            logger.info(f"[중복 방지] {event_date} 날짜의 기존 데이터 삭제 완료: {query_job.num_dml_affected_rows}행")
        except Exception as e:
            logger.warning(f"[중복 방지] 기존 데이터 삭제 중 오류 (계속 진행): {e}")
