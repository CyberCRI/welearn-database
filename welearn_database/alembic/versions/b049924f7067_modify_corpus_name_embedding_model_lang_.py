"""modify corpus_name_embedding_model_lang view

Revision ID: b049924f7067
Revises: f8602200fa99
Create Date: 2026-03-31 16:09:12.085443

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b049924f7067"
down_revision: Union[str, None] = "f8602200fa99"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DROP MATERIALIZED VIEW corpus_related.corpus_name_embedding_model_lang;
        """
    )
    op.execute(
        """

CREATE MATERIALIZED VIEW corpus_related.corpus_name_embedding_model_lang
TABLESPACE pg_default
AS WITH ranked AS (
SELECT
    c.source_name,
    cem.corpus_id,
    cem.embedding_model_id,
    em.title,
    em.lang,
    cem.used_since,
    c.category_id,
    ROW_NUMBER() OVER (
      PARTITION BY cem.corpus_id,
    em.lang
ORDER BY
    cem.used_since DESC
    ) AS rn
FROM
    corpus_related.corpus_embedding_model cem
JOIN corpus_related.corpus c ON
    c.id = cem.corpus_id
JOIN corpus_related.embedding_model em ON
    em.id = cem.embedding_model_id
WHERE
    c.is_active
)
    SELECT
        source_name,
        corpus_id,
        embedding_model_id,
        title,
        lang,
        used_since,
        category_id
    FROM
        ranked
    WHERE
        rn = 1
        
WITH DATA;
    """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP MATERIALIZED VIEW corpus_related.corpus_name_embedding_model_lang;
        """
    )
    op.execute(
        """
        CREATE MATERIALIZED VIEW corpus_related.corpus_name_embedding_model_lang
        TABLESPACE pg_default
        AS SELECT corpus.source_name,
            embedding_model.title,
            embedding_model.lang
           FROM corpus_related.corpus
             JOIN corpus_related.corpus_embedding_model ON corpus_embedding_model.corpus_id = corpus.id
             JOIN corpus_related.embedding_model ON embedding_model.id = corpus_embedding_model.embedding_model_id
          WHERE corpus.is_active
        WITH DATA;
        """
    )
