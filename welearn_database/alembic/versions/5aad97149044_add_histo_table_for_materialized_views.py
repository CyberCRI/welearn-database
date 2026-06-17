"""add_histo_table_for_materialized_views

Revision ID: 5aad97149044
Revises: b84462ca3800
Create Date: 2026-06-17 11:31:55.292978

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5aad97149044"
down_revision: Union[str, None] = "b84462ca3800"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "historical_qty_document_per_corpus",
        sa.Column(
            "id", sa.Uuid(), server_default=text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("source_name", sa.String(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", postgresql.TIMESTAMP(), server_default="NOW()", nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="document_related",
    )

    op.create_table(
        "historical_qty_document_in_qdrant_per_corpus",
        sa.Column(
            "id", sa.Uuid(), server_default=text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("source_name", sa.String(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", postgresql.TIMESTAMP(), server_default="NOW()", nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="document_related",
    )

    op.create_table(
        "historical_qty_document_in_qdrant",
        sa.Column(
            "id", sa.Uuid(), server_default=text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", postgresql.TIMESTAMP(), server_default="NOW()", nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="document_related",
    )


def downgrade() -> None:
    op.drop_table("historical_qty_document_per_corpus", schema="document_related")
    op.drop_table(
        "historical_qty_document_in_qdrant_per_corpus", schema="document_related"
    )
    op.drop_table("historical_qty_document_in_qdrant", schema="document_related")
