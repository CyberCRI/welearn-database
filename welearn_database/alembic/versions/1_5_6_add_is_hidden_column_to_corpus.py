"""add_is hidden_column_to_corpus

Revision ID: 1_5_6
Revises: 1_5_5
Create Date: 2026-10-28 17:17:28.966030

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
    op.add_column("corpus", sa.Column("is_hidden", sa.Boolean(), nullable=False, server_default=sa.false()), schema="corpus_related")


def downgrade() -> None:
    op.drop_column("corpus", "is_hidden", schema="corpus_related")
