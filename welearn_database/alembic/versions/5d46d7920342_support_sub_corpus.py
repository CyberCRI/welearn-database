"""support_sub_corpus

Revision ID: 5d46d7920342
Revises: 95ffe7afa64c
Create Date: 2026-09-21 14:47:28.116941

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5d46d7920342"
down_revision: Union[str, None] = "95ffe7afa64c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "corpus",
        sa.Column("parent_corpus_id", sa.Uuid(), nullable=True),
        schema="corpus_related",
    )
    op.create_foreign_key(
        "corpus_parent_corpus_id_fkey",
        "corpus",
        "corpus",
        ["parent_corpus_id"],
        ["id"],
        source_schema="corpus_related",
        referent_schema="corpus_related",
    )
    op.execute("DROP VIEW grafana.corpus")
    op.drop_column("corpus", "binary_treshold", schema="corpus_related")
    op.execute("""
            CREATE OR REPLACE VIEW grafana.corpus
            AS SELECT corpus.id,
            corpus.parent_corpus_id,
            corpus.source_name,
            corpus.main_url,
            corpus.is_fix,
            corpus.is_active,
            corpus.category_id
           FROM corpus_related.corpus;
    """)


def downgrade() -> None:
    op.drop_constraint(
        "corpus_parent_corpus_id_fkey", "corpus", schema="corpus_related"
    )
    op.execute("DROP VIEW grafana.corpus")
    op.drop_column("corpus", "parent_corpus_id", schema="corpus_related")
    op.add_column(
        "corpus",
        sa.Column(
            "binary_treshold",
            sa.Float(),
            nullable=False,
            default=0.5,
            server_default="0.5",
        ),
        schema="corpus_related",
    )
    op.execute("""
            CREATE OR REPLACE VIEW grafana.corpus
            AS SELECT corpus.id,
            corpus.source_name,
            corpus.is_fix,
            corpus.binary_treshold
           FROM corpus_related.corpus;
    """)
