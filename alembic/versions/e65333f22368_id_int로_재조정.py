"""id > int로 재조정

Revision ID: e65333f22368
Revises: 5b548ef6dc47
Create Date: 2025-05-24 20:43:54.708545

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "e65333f22368"
down_revision: Union[str, None] = "5b548ef6dc47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 버전이 꼬여서 임시 조치
def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
