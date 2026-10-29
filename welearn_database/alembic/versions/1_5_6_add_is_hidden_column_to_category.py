"""add_is hidden_column_to_category

Revision ID: 1_5_6
Revises: 1_5_6
Create Date: 2026-10-29 16:05:28.280023

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1_5_6'
down_revision: Union[str, None] = '1_5_5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
