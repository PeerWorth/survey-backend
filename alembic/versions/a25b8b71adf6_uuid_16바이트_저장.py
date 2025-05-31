"""uuid 16바이트 저장

Revision ID: a25b8b71adf6
Revises: d22ec8b90395
Create Date: 2025-05-24 20:24:33.866390

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "a25b8b71adf6"
down_revision: Union[str, None] = "d22ec8b90395"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 버전이 꼬여서 임시 조치
def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
