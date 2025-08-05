"""Rename monthly_rent to is_monthly_rent in user_profile table

Revision ID: 57bbb5ca3f2d
Revises: 6213a7491fb9
Create Date: 2025-08-05 09:56:33.478044

"""

from typing import Sequence, Union

from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "57bbb5ca3f2d"
down_revision: Union[str, None] = "6213a7491fb9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename column from monthly_rent to is_monthly_rent
    op.alter_column(
        "user_profile",
        "monthly_rent",
        new_column_name="is_monthly_rent",
        existing_type=mysql.TINYINT(display_width=1),
        existing_nullable=True,
        existing_comment="월세 여부",
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Rename column back from is_monthly_rent to monthly_rent
    op.alter_column(
        "user_profile",
        "is_monthly_rent",
        new_column_name="monthly_rent",
        existing_type=mysql.TINYINT(display_width=1),
        existing_nullable=True,
        existing_comment="월세 여부",
    )
