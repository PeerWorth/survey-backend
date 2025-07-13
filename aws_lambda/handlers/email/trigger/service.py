from constants import MAX_SINGLE_SEND_SIZE
from repository import TriggerRepository

from aws_lambda.shared.db_config import get_session

# from shared.db_config import get_session


class EmailTargetService:
    def __init__(self, repository: TriggerRepository, session):
        self.repository = repository
        self.session = session

    @classmethod
    async def create(cls):
        session = await get_session()
        repo = TriggerRepository(session)
        return cls(repository=repo, session=session)

    async def get_target_emails(self) -> list[list[tuple[int, str]]]:
        try:
            emails: list[tuple[int, str]] = await self.repository.get_agreed_emails()
            return self._chunk_list(emails)
        finally:
            await self.session.close()

    def _chunk_list(self, emails: list[tuple[int, str]]) -> list[list[tuple[int, str]]]:
        return [emails[i : i + MAX_SINGLE_SEND_SIZE] for i in range(0, len(emails), MAX_SINGLE_SEND_SIZE)]
