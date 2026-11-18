"""add feature, thread and guest_feature_usage tables

Revision ID: 1_5_7
Revises: 1_5_6
Create Date: 2026-11-18 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1_5_7'
down_revision: Union[str, None] = '1_5_6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "user_related"

# created here so every environment has the same rows; code finds them by title
FEATURE_TITLES = ["chat", "microlearning", "syllabus"]


def upgrade() -> None:
    feature = op.create_table(
        "feature",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("title", name="feature_title_key"),
        schema=SCHEMA,
    )
    op.bulk_insert(feature, [{"title": title} for title in FEATURE_TITLES])

    op.create_table(
        "thread",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("inferred_user_id", sa.Uuid(), nullable=False),
        sa.Column("feature_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("current_step", sa.Integer(), nullable=True),
        sa.Column("max_step", sa.Integer(), nullable=True),
        sa.Column("is_finished", sa.Boolean(), server_default=sa.false(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["inferred_user_id"],
            [f"{SCHEMA}.inferred_user.id"],
            name="thread_inferred_user_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["feature_id"],
            [f"{SCHEMA}.feature.id"],
            name="thread_feature_id_fkey",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "thread_user_feature_updated_idx",
        "thread",
        ["inferred_user_id", "feature_id", sa.text("updated_at DESC")],
        schema=SCHEMA,
    )

    op.create_table(
        "guest_feature_usage",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("inferred_user_id", sa.Uuid(), nullable=False),
        sa.Column("feature_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["inferred_user_id"],
            [f"{SCHEMA}.inferred_user.id"],
            name="guest_feature_usage_inferred_user_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["feature_id"],
            [f"{SCHEMA}.feature.id"],
            name="guest_feature_usage_feature_id_fkey",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "guest_feature_usage_user_feature_action_created_idx",
        "guest_feature_usage",
        ["inferred_user_id", "feature_id", "action", "created_at"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "guest_feature_usage_user_feature_action_created_idx",
        table_name="guest_feature_usage",
        schema=SCHEMA,
    )
    op.drop_table("guest_feature_usage", schema=SCHEMA)
    op.drop_index("thread_user_feature_updated_idx", table_name="thread", schema=SCHEMA)
    op.drop_table("thread", schema=SCHEMA)
    op.drop_table("feature", schema=SCHEMA)
