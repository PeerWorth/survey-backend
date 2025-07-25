import logging

from constant import BIGQUERY_USER_TABLE
from google.cloud import bigquery
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

    async def insert_to_bigquery(self, rows: list[dict]):
        client = bigquery.Client()

        errors = client.insert_rows_json(BIGQUERY_USER_TABLE, rows)

        if errors:
            logging.error(f"BigQuery insert 실패: {errors}")
            raise Exception(f"BigQuery insert 실패: {errors}")
        else:
            logging.info(f"{len(rows)}개 행이 BigQuery에 성공적으로 삽입되었습니다.")
