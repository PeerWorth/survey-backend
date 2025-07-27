import logging

from constant import BIGQUERY_USER_TABLE, MAX_ROWS_PER_REQUEST
from google.cloud import bigquery
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
        client = bigquery.Client()

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
