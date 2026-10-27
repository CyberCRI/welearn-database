"""analytical_view_for_research

Revision ID: 1_5_5
Revises: d990f127902f
Create Date: 2026-10-19 15:04:47.681660

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1_5_5"
down_revision: Union[str, None] = "d990f127902f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE OR REPLACE VIEW grafana.conversation_info
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
            cm.original_feature_name = 'chat';
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS grafana.conversation_info;")
