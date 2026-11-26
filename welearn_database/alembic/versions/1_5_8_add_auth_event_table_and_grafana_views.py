"""add auth_event table and its grafana views

Revision ID: 1_5_8
Revises: 1_5_7
Create Date: 2026-11-26 17:36:17.512738

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1_5_8'
down_revision: Union[str, None] = '1_5_7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "user_related"

# written out rather than read from AuthEventType, so this revision keeps
# creating the same constraint if the enum changes later
EVENT_TYPES = ["signup", "account_created", "login", "logout"]


def upgrade() -> None:
    op.create_table(
        "auth_event",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("inferred_user_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=True),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("identity_provider", sa.String(), nullable=True),
        sa.Column("is_limited_access", sa.Boolean(), nullable=True),
        sa.Column("keycloak_session_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        # a CHECK rather than a Postgres ENUM, so adding a value is a simple migration
        sa.CheckConstraint(
            "event_type IN (" + ", ".join(f"'{t}'" for t in EVENT_TYPES) + ")",
            name="auth_event_event_type_check",
        ),
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
    op.create_index("auth_event_created_at_idx", "auth_event", ["created_at"], schema=SCHEMA)
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
        postgresql_where=sa.text("event_type = 'login' AND keycloak_session_id IS NOT NULL"),
    )

    # keycloak_session_id is left out: dashboards don't need it
    op.execute("""
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
    """)
    # provider labels the NULL identity_provider (email/password or unknown) so
    # it shows up as its own series in Grafana
    op.execute("""
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
    """)


def downgrade() -> None:
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
