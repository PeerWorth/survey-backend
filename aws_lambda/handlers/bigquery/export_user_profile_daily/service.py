import logging

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
            rows = await self.repository.get_user_profiles()
            logger.info(f"Fetched {len(rows)} user profile records.")
            return rows
        finally:
            await self.session.close()
