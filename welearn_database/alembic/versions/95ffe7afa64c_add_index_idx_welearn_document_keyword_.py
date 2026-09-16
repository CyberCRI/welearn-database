"""add_index_idx_welearn_document_keyword_document_id

Revision ID: 95ffe7afa64c
Revises: f5e91a5c950d
Create Date: 2026-09-16 15:44:06.977345

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "95ffe7afa64c"
down_revision: Union[str, None] = "f5e91a5c950d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "idx_welearn_document_keyword_document_id",
        "welearn_document_keyword",
        ["welearn_document_id"],
        schema="document_related",
    )


def downgrade() -> None:
    op.drop_index(
        "idx_welearn_document_keyword_document_id",
        table_name="document_keyword",
        schema="document_related",
    )
