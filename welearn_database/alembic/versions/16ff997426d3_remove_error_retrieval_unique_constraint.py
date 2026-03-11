"""Remove error retrieval unique constraint

Revision ID: 16ff997426d3
Revises: a50a1db3ca2a
Create Date: 2025-06-02 14:23:49.689745

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "16ff997426d3"
down_revision: Union[str, None] = "a50a1db3ca2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "error_retrieval_document_id_http_error_code_idx",
        "error_retrieval",
        type_="unique",
        schema="document_related",
    )


def downgrade() -> None:
    op.create_index(
        "error_retrieval_document_id_http_error_code_idx",
        "error_retrieval",
        ["document_id", "http_error_code"],
        unique=True,
        schema="document_related",
    )
