"""add referrer origin column to user and session

Revision ID: 068312e7800c
Revises: 4f5a188dd614
Create Date: 2026-01-12 11:45:40.359740

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "068312e7800c"
down_revision: Union[str, None] = "4f5a188dd614"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "session",
        sa.Column("origin_referrer", sa.String(), nullable=True),
        schema="user_related",
    )
    op.add_column(
        "inferred_user",
        sa.Column("origin_referrer", sa.String(), nullable=True),
        schema="user_related",
    )


def downgrade() -> None:
    op.drop_column(
        "inferred_user",
        "origin_referrer",
        schema="user_related",
    )
    op.drop_column(
        "session",
        "origin_referrer",
        schema="user_related",
    )
