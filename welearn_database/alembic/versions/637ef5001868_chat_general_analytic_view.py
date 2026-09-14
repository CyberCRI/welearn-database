"""chat_general_analytic_view

Revision ID: 637ef5001868
Revises: f5e91a5c950d
Create Date: 2026-09-14 18:17:42.736006

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "637ef5001868"
down_revision: Union[str, None] = "f5e91a5c950d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE OR REPLACE VIEW grafana.chat_general_analytic
    AS WITH conversation_info AS (
SELECT
	DISTINCT ON
	(cm.conversation_id) cm.conversation_id,
	created_at
FROM
	user_related.chat_message cm
ORDER BY
	cm.conversation_id,
	cm.created_at ASC
),
qty_docs AS (
SELECT
	message_id,
	COUNT(1) AS "count"
FROM
	user_related.returned_document rd
GROUP BY
	rd.message_id 
)
SELECT
	id AS "message_id",
	cm.textual_content,
	cm.conversation_id,
	ci.created_at AS "conversation_started",
	cm."role",
	CASE
		cm."role"
		WHEN 'user' THEN NULL
		ELSE COALESCE(qd.count, 0)
	END AS "number_of_sources"
FROM
	user_related.chat_message cm
INNER JOIN conversation_info ci ON
	ci.conversation_id = cm.conversation_id
FULL JOIN qty_docs qd ON
	qd.message_id = cm.id
WHERE
	cm.original_feature_name = 'chat'
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS grafana.chat_general_analytic;")
