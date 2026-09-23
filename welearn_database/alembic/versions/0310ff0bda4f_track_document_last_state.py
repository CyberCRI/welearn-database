"""track_document_last_state

Revision ID: 0310ff0bda4f
Revises: d22d6324c256
Create Date: 2026-09-23 11:48:30.473174

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0310ff0bda4f"
down_revision: Union[str, None] = "d22d6324c256"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE OR REPLACE VIEW document_related.track_document_latest_state
    AS SELECT DISTINCT ON (ps.document_id) ps.id,
        ps.document_id,
        wd.corpus_id,
        wd.lang,
        ps.title,
        ps.created_at,
        ps.operation_order
       FROM document_related.process_state ps
         JOIN document_related.welearn_document wd ON ps.document_id = wd.id
      ORDER BY ps.document_id, ps.operation_order DESC;
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS document_related.track_document_latest_state;")
