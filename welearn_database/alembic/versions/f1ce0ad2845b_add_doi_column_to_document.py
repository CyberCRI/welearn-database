"""add doi column to document

Revision ID: f1ce0ad2845b
Revises: f8602200fa99
Create Date: 2026-04-29 15:39:51.079086

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1ce0ad2845b"
down_revision: Union[str, None] = "b049924f7067"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "welearn_document",
        sa.Column("doi", sa.String(), nullable=True, unique=True),
        schema="document_related",
    )


def downgrade() -> None:
    op.drop_column("welearn_document", "doi", schema="document_related")
