"""job 테이블 english 필드 제거

Revision ID: 6213a7491fb9
Revises: e65333f22368
Create Date: 2025-05-31 19:57:17.171217

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6213a7491fb9"
down_revision: Union[str, None] = "e65333f22368"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("job") as batch_op:
        batch_op.drop_column("name_en")


def downgrade() -> None:
    with op.batch_alter_table("job") as batch_op:
        batch_op.add_column(sa.Column("name_en", sa.String(), nullable=True))
