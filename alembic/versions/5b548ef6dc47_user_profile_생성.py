"""user profile 생성

Revision ID: 5b548ef6dc47
Revises: a25b8b71adf6
Create Date: 2025-05-24 20:37:45.837822

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "5b548ef6dc47"
down_revision: Union[str, None] = "a25b8b71adf6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 버전이 꼬여서 임시 조치
def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
