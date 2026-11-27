"""add auth_event table, its grafana views and the grafana usage views

Revision ID: 1_5_8
Revises: 1_5_7
Create Date: 2026-11-26 17:36:17.512738

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "1_5_8"
down_revision: Union[str, None] = "1_5_7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "user_related"

# written out rather than read from AuthEventType, so this revision keeps
# creating the same type if the enum changes later
EVENT_TYPES = ["signup", "account_created", "login", "logout"]

# the API paths (endpoint_request.endpoint_name) of each feature, as LIKE
# patterns that don't overlap, so a request gets one feature at most. Paths not
# listed (session, guest quota, access, logout, metrics, health, the lists
# loaded when the app starts...) are plumbing and have no feature.
ENDPOINT_FEATURES = [
    # a question asked; history and threads are loaded on boot, so left out
    ("/api/v1/qna/chat/agent", "chat"),
    ("/api/v1/qna/chat/agent_stream", "chat"),
    ("/api/v1/qna/chat/answer", "chat"),
    ("/api/v1/qna/stream", "chat"),
    ("/api/v1/qna/reformulate/%", "chat"),
    ("/api/v1/search/by_document", "search"),
    ("/api/v1/search/by_slices", "search"),
    ("/api/v1/search/multiple_by_slices", "search"),
    ("/api/v1/search/collections/%", "search"),
    # the client sends it with each search, to show the query's SDGs
    ("/api/v1/search/sdg_classify", "sdg detection"),
    ("/api/v1/tutor/files/content", "syllabus (from scratch)"),
    ("/api/v1/tutor/search_extracts", "syllabus (from scratch)"),
    ("/api/v1/tutor/search_datasets", "syllabus (from scratch)"),
    ("/api/v1/tutor/syllabus", "syllabus (from scratch)"),
    ("/api/v1/tutor/syllabus/feedback", "syllabus (from scratch)"),
    ("/api/v1/tutor/syllabus/user_update", "syllabus (from scratch)"),
    ("/api/v1/tutor/course/%", "syllabus v2 (existing course)"),
    # the hidden /tutor_test page and the steps it calls
    ("/api/v1/tutor/mas_files/%", "syllabus (test page)"),
    ("/api/v1/tutor/api/%", "syllabus (test page)"),
    ("/api/v1/tutor/syllabus/description", "syllabus (test page)"),
    ("/api/v1/tutor/syllabus/learning_objectives", "syllabus (test page)"),
    ("/api/v1/tutor/syllabus/learning_outcomes", "syllabus (test page)"),
    ("/api/v1/tutor/syllabus/competency_map", "syllabus (test page)"),
    ("/api/v1/tutor/syllabus/sustainability_integration", "syllabus (test page)"),
    # a bookmark added or removed; the bare list is loaded on boot
    ("/api/v1/user/bookmarks/%", "bookmarks"),
    ("/api/v1/user/%/bookmarks/%", "bookmarks"),
    ("/api/v1/bibliography/%", "bibliography export"),
    ("/api/v1/micro_learning/%", "learn (microlearning)"),
    ("/api/v1/user/university-request", "university request"),
]

# a guest who logs in later gets its keycloak_id on the same row, so it counts
# as an account for its past too
USER_KIND = "CASE WHEN iu.keycloak_id IS NULL THEN 'guest' ELSE 'account' END"

# 6d4346fad6f4's definition, restored as is by the downgrade
OLD_USED_FEATURE_PER_SESSION = """
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
        """


def _comment(view: str, text: str) -> None:
    op.execute(f"COMMENT ON VIEW grafana.{view} IS '{text}';")


def upgrade() -> None:
    op.create_table(
        "auth_event",
        sa.Column(
            "id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("inferred_user_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=True),
        sa.Column(
            "event_type",
            postgresql.ENUM(*EVENT_TYPES, name="auth_event_type", schema=SCHEMA),
            nullable=False,
        ),
        sa.Column("identity_provider", sa.String(), nullable=True),
        sa.Column("is_limited_access", sa.Boolean(), nullable=True),
        sa.Column("keycloak_session_id", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["inferred_user_id"],
            [f"{SCHEMA}.inferred_user.id"],
            name="auth_event_inferred_user_id_fkey",
            ondelete="CASCADE",
        ),
        # events outlive a purged session, they only lose its host
        sa.ForeignKeyConstraint(
            ["session_id"],
            [f"{SCHEMA}.session.id"],
            name="auth_event_session_id_fkey",
            ondelete="SET NULL",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "auth_event_created_at_idx", "auth_event", ["created_at"], schema=SCHEMA
    )
    op.create_index(
        "auth_event_event_type_created_at_idx",
        "auth_event",
        ["event_type", "created_at"],
        schema=SCHEMA,
    )
    # one login per Keycloak session: a concurrent second insert fails here
    op.create_index(
        "auth_event_login_keycloak_session_key",
        "auth_event",
        ["inferred_user_id", "keycloak_session_id"],
        unique=True,
        schema=SCHEMA,
        postgresql_where=sa.text(
            "event_type = 'login' AND keycloak_session_id IS NOT NULL"
        ),
    )

    # keycloak_session_id is left out: dashboards don't need it
    op.execute(
        """
CREATE OR REPLACE VIEW grafana.auth_event
AS SELECT auth_event.id,
    auth_event.inferred_user_id,
    auth_event.session_id,
    auth_event.event_type,
    auth_event.identity_provider,
    auth_event.is_limited_access,
    auth_event.created_at,
    session.host
   FROM user_related.auth_event
     LEFT JOIN user_related.session ON session.id = auth_event.session_id;
    """
    )
    # provider labels the NULL identity_provider (email/password or unknown) so
    # it shows up as its own series in Grafana
    op.execute(
        """
CREATE OR REPLACE VIEW grafana.auth_event_daily
AS SELECT date_trunc('day', auth_event.created_at) AS day,
    auth_event.event_type,
    auth_event.identity_provider,
    COALESCE(auth_event.identity_provider, 'email_or_unknown') AS provider,
    auth_event.is_limited_access,
    count(*) AS events,
    count(DISTINCT auth_event.inferred_user_id) AS users
   FROM user_related.auth_event
  GROUP BY date_trunc('day', auth_event.created_at),
    auth_event.event_type,
    auth_event.identity_provider,
    auth_event.is_limited_access;
    """
    )

    values = ",\n    ".join(
        f"('{pattern}', '{feature}')" for pattern, feature in ENDPOINT_FEATURES
    )
    op.execute(
        f"""
CREATE OR REPLACE VIEW grafana.endpoint_feature
AS SELECT endpoint_feature.endpoint_pattern,
    endpoint_feature.feature
   FROM (VALUES
    {values}
  ) AS endpoint_feature(endpoint_pattern, feature);
    """
    )
    _comment(
        "endpoint_feature",
        "The feature of each API path, as a LIKE pattern on "
        "endpoint_request.endpoint_name; other paths are plumbing.",
    )
    op.execute(
        f"""
CREATE OR REPLACE VIEW grafana.feature_request
AS SELECT er.id,
    er.session_id,
    s.inferred_user_id,
    {USER_KIND} AS user_kind,
    ef.feature,
    er.created_at
   FROM user_related.endpoint_request er
     JOIN grafana.endpoint_feature ef ON er.endpoint_name LIKE ef.endpoint_pattern
     JOIN user_related.session s ON s.id = er.session_id
     JOIN user_related.inferred_user iu ON iu.id = s.inferred_user_id;
    """
    )
    _comment(
        "feature_request",
        "The API requests that use a feature (see endpoint_feature), with their "
        "user. user_kind is guest when the user has no account today.",
    )
    op.execute(
        f"""
CREATE OR REPLACE VIEW grafana.active_user_day
AS SELECT date_trunc('day', er.created_at) AS day,
    s.inferred_user_id,
    {USER_KIND} AS user_kind,
    count(*) AS requests
   FROM user_related.endpoint_request er
     JOIN user_related.session s ON s.id = er.session_id
     JOIN user_related.inferred_user iu ON iu.id = s.inferred_user_id
  GROUP BY (date_trunc('day', er.created_at)), s.inferred_user_id, iu.keycloak_id;
    """
    )
    _comment(
        "active_user_day",
        "One row per user and day with at least one API request. user_kind is "
        "guest when the user has no account today: a guest who logs in later "
        "counts as an account for its past days too.",
    )
    op.execute(
        """
CREATE OR REPLACE VIEW grafana.active_users_daily
AS SELECT active_user_day.day,
    active_user_day.user_kind,
    count(*) AS active_users,
    sum(active_user_day.requests)::bigint AS requests
   FROM grafana.active_user_day
  GROUP BY active_user_day.day, active_user_day.user_kind;
    """
    )
    _comment(
        "active_users_daily",
        "Users with at least one API request per day, guests and accounts "
        "(see active_user_day). Days cannot be summed: count distinct users "
        "of active_user_day over a range instead.",
    )
    op.execute(
        """
CREATE OR REPLACE VIEW grafana.new_users_daily
AS SELECT date_trunc('day', inferred_user.created_at) AS day,
    count(*) AS new_users,
    count(inferred_user.keycloak_id) AS with_account
   FROM user_related.inferred_user
  GROUP BY (date_trunc('day', inferred_user.created_at));
    """
    )
    _comment(
        "new_users_daily",
        "Users (inferred_user rows) created per day, and how many of them have "
        "an account today.",
    )
    op.execute(
        """
CREATE OR REPLACE VIEW grafana.feature_usage_daily
AS SELECT date_trunc('day', feature_request.created_at) AS day,
    feature_request.feature,
    feature_request.user_kind,
    count(DISTINCT feature_request.inferred_user_id) AS users,
    count(*) AS requests
   FROM grafana.feature_request
  GROUP BY (date_trunc('day', feature_request.created_at)),
    feature_request.feature,
    feature_request.user_kind;
    """
    )
    _comment(
        "feature_usage_daily",
        "Distinct users and requests per day, feature and user_kind (see "
        "feature_request). Days cannot be summed for users.",
    )
    op.execute(
        """
CREATE OR REPLACE VIEW grafana.guest_limit_hit
AS SELECT guest_feature_usage.id,
    guest_feature_usage.inferred_user_id,
    feature.title AS feature,
    guest_feature_usage.created_at
   FROM user_related.guest_feature_usage
     JOIN user_related.feature ON feature.id = guest_feature_usage.feature_id
  WHERE guest_feature_usage.action = 'quota_exceeded';
    """
    )
    _comment(
        "guest_limit_hit",
        "Each time a guest was refused a use of a feature (feature table title) "
        "because its daily quota was used up.",
    )
    op.execute(
        """
CREATE OR REPLACE VIEW grafana.guest_limit_hits_daily
AS SELECT date_trunc('day', guest_limit_hit.created_at) AS day,
    guest_limit_hit.feature,
    count(DISTINCT guest_limit_hit.inferred_user_id) AS users,
    count(*) AS refusals
   FROM grafana.guest_limit_hit
  GROUP BY (date_trunc('day', guest_limit_hit.created_at)), guest_limit_hit.feature;
    """
    )
    _comment(
        "guest_limit_hits_daily",
        "Guests refused for a used-up quota, and refusals, per day and feature "
        "(see guest_limit_hit). Days cannot be summed for users.",
    )
    # same columns as 6d4346fad6f4, so its panels keep working; it now uses the
    # current paths and matches a bookmark path with its document id
    op.execute(
        """
CREATE OR REPLACE VIEW grafana.used_feature_per_session
AS WITH used AS (
         SELECT feature_request.session_id,
            feature_request.feature,
            count(*) AS cnt
           FROM grafana.feature_request
          GROUP BY feature_request.session_id, feature_request.feature
        ), features AS (
         SELECT DISTINCT endpoint_feature.feature
           FROM grafana.endpoint_feature
        ), sessions AS (
         SELECT DISTINCT endpoint_request.session_id
           FROM user_related.endpoint_request
        )
 SELECT s.inferred_user_id,
    sessions.session_id,
    features.feature AS feature_name,
    COALESCE(used.cnt, 0::bigint) AS cnt,
    COALESCE(used.cnt, 0::bigint) > 0 AS is_feature_used,
    s.created_at AS session_created_at
   FROM sessions
     CROSS JOIN features
     JOIN user_related.session s ON s.id = sessions.session_id
     LEFT JOIN used ON used.session_id = sessions.session_id
       AND used.feature = features.feature;
    """
    )
    _comment(
        "used_feature_per_session",
        "One row per session with API requests and per feature (see "
        "endpoint_feature): cnt requests, is_feature_used when cnt > 0.",
    )


def downgrade() -> None:
    # back to its old definition first, so the views it used can be dropped
    op.execute(OLD_USED_FEATURE_PER_SESSION)
    op.execute("COMMENT ON VIEW grafana.used_feature_per_session IS NULL;")
    op.execute("DROP VIEW IF EXISTS grafana.guest_limit_hits_daily;")
    op.execute("DROP VIEW IF EXISTS grafana.guest_limit_hit;")
    op.execute("DROP VIEW IF EXISTS grafana.feature_usage_daily;")
    op.execute("DROP VIEW IF EXISTS grafana.new_users_daily;")
    op.execute("DROP VIEW IF EXISTS grafana.active_users_daily;")
    op.execute("DROP VIEW IF EXISTS grafana.active_user_day;")
    op.execute("DROP VIEW IF EXISTS grafana.feature_request;")
    op.execute("DROP VIEW IF EXISTS grafana.endpoint_feature;")
    op.execute("DROP VIEW IF EXISTS grafana.auth_event_daily;")
    op.execute("DROP VIEW IF EXISTS grafana.auth_event;")
    op.drop_index(
        "auth_event_login_keycloak_session_key", table_name="auth_event", schema=SCHEMA
    )
    op.drop_index(
        "auth_event_event_type_created_at_idx", table_name="auth_event", schema=SCHEMA
    )
    op.drop_index("auth_event_created_at_idx", table_name="auth_event", schema=SCHEMA)
    op.drop_table("auth_event", schema=SCHEMA)
    op.execute(f"DROP TYPE IF EXISTS {SCHEMA}.auth_event_type;")
