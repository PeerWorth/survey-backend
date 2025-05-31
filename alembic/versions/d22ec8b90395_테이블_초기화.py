"""테이블 초기화

Revision ID: d22ec8b90395
Revises:
Create Date: 2025-05-20 16:05:46.823443

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "d22ec8b90395"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 버전이 꼬여서 임시 조치
def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
