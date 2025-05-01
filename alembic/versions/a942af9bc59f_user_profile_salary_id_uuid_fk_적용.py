"""user_profile salary id uuid FK 적용

Revision ID: a942af9bc59f
Revises: 499158777778
Create Date: 2025-05-01 18:26:29.190412

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a942af9bc59f"
down_revision: Union[str, None] = "499158777778"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing foreign key constraint on user_profile.salary_id
    op.drop_constraint("user_profile_ibfk_1", "user_profile", type_="foreignkey")

    # Alter columns to BINARY(16)
    op.alter_column(
        "user_profile", "salary_id", existing_type=mysql.INTEGER(), type_=sa.BINARY(length=16), existing_nullable=False
    )
    op.alter_column(
        "user_salary", "id", existing_type=mysql.INTEGER(), type_=sa.BINARY(length=16), existing_nullable=False
    )

    # Recreate foreign key constraint
    op.create_foreign_key(
        "user_profile_salary_id_fkey", "user_profile", "user_salary", ["salary_id"], ["id"], ondelete="CASCADE"
    )


def downgrade() -> None:
    # Drop the FK we created
    op.drop_constraint("user_profile_salary_id_fkey", "user_profile", type_="foreignkey")

    # Revert columns back to INTEGER
    op.alter_column(
        "user_salary", "id", existing_type=sa.BINARY(length=16), type_=mysql.INTEGER(), existing_nullable=False
    )
    op.alter_column(
        "user_profile", "salary_id", existing_type=sa.BINARY(length=16), type_=mysql.INTEGER(), existing_nullable=False
    )

    # Recreate original foreign key constraint
    op.create_foreign_key(
        "user_profile_ibfk_1", "user_profile", "user_salary", ["salary_id"], ["id"], ondelete="CASCADE"
    )
