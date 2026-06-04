"""update grafana process state view

Revision ID: b84462ca3800
Revises: 8b780aea403a
Create Date: 2026-06-04 16:56:18.693751

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b84462ca3800"
down_revision: Union[str, None] = "8b780aea403a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE OR REPLACE VIEW grafana.process_state
        AS SELECT process_state.id,
        process_state.document_id,
        process_state.title,
        process_state.created_at,
        process_state.operation_order,
        corpus.source_name
           FROM document_related.process_state
             JOIN document_related.welearn_document ON welearn_document.id = process_state.document_id
             JOIN corpus_related.corpus ON welearn_document.corpus_id = corpus.id;
        """)


def downgrade() -> None:
    op.execute("""
        CREATE OR REPLACE VIEW grafana.process_state
        AS SELECT process_state.id,
        process_state.document_id,
        process_state.title,
        process_state.created_at,
        process_state.operation_order,
           FROM document_related.process_state;
        """)
