"""view_used_feature_per_session

Revision ID: 6d4346fad6f4
Revises: 5aad97149044
Create Date: 2026-06-17 11:54:52.441998

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6d4346fad6f4"
down_revision: Union[str, None] = "5aad97149044"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE OR REPLACE VIEW grafana.used_feature_per_session
        AS WITH matching_features_endpoint AS (
SELECT
	endpoint_name,
	feature_name
FROM
	(
VALUES
	('/api/v1/search/by_document', 'search'),
	('/api/v1/qna/chat/answer', 'chat'),
	('/api/v1/qna/chat/agent', 'chat'),
	('/api/v1/tutor/syllabus', 'syllabus'),
	('/api/v1/user/bookmarks/' || ':' || 'document_id', 'bookmark'),
	('/api/v1/user/' || ':' || 'user_id' || '/bookmarks/' || ':' || 'document_id', 'bookmark')
	) AS t(endpoint_name, feature_name)
),
session_feature_pair AS (
SELECT
	DISTINCT
	er.session_id,
	mfe.feature_name
FROM
	user_related.endpoint_request er
CROSS JOIN matching_features_endpoint mfe
ORDER BY
	er.session_id
),
actual_count AS (
SELECT
	er.session_id,
	mfe.feature_name,
	COUNT(1) AS cnt
FROM
	user_related.endpoint_request er
INNER JOIN
	user_related."session" s ON
	s.id = er.session_id
INNER JOIN
	matching_features_endpoint mfe ON
	mfe.endpoint_name = er.endpoint_name
GROUP BY
	er.session_id,
	mfe.feature_name 
)
SELECT 
	s.inferred_user_id,
	sfp.session_id,
	sfp.feature_name,
	COALESCE(ac.cnt, 0) AS cnt,
	COALESCE(ac.cnt, 0) > 0 AS is_feature_used,
	s.created_at AS session_created_at
FROM
	session_feature_pair sfp
LEFT JOIN actual_count ac ON
	ac.feature_name = sfp.feature_name
	AND ac.session_id = sfp.session_id
INNER JOIN user_related."session" s ON
	s.id = sfp.session_id
ORDER BY
	session_created_at
        """)


def downgrade() -> None:
    op.execute("""
    DROP VIEW IF EXISTS grafana.used_feature_per_session;
    """)
