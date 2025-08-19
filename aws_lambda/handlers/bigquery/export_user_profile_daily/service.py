import json
import logging
import os

from config import get_config
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
        self.config = get_config()

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

        chunks = list(chunked(rows, self.config.MAX_ROWS_PER_REQUEST))
        total_success = 0

        for idx, chunk in enumerate(chunks):
            errors = client.insert_rows_json(self.config.BIGQUERY_USER_TABLE, chunk)
            if errors:
                logger.error(f"[Chunk {idx + 1}/{len(chunks)}] 일부 행 insert 실패: {errors}")
            else:
                logger.info(f"[Chunk {idx + 1}/{len(chunks)}] {len(chunk)}개 행 삽입 성공")
                total_success += len(chunk)

        logger.info(f"[BigQuery Insert 완료] {event_date} - 총 삽입 성공: {total_success} / 전체: {len(rows)}")

    def _get_credentials(self):
        gcp_key_json = os.environ.get(self.config.CREDENTIALS_ENV_VAR)
        if gcp_key_json:
            try:
                key_data = json.loads(gcp_key_json)
                return service_account.Credentials.from_service_account_info(key_data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 오류: {e}")
                raise

        logger.warning("Google Cloud 인증 정보가 설정되지 않았습니다. 기본 인증을 사용합니다.")
        return None
