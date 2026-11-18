"""add guest_feature_usage table

Revision ID: 1_5_8
Revises: 1_5_7
Create Date: 2026-11-18 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert


# revision identifiers, used by Alembic.
revision: str = '1_5_8'
down_revision: Union[str, None] = '1_5_7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "user_related"

# the features with guest quotas; "chat" comes with 1_5_7. The quotas inside a
# feature (generate, feedback, files...) are the rows' action, not features
NEW_FEATURE_TITLES = ["syllabus"]


def upgrade() -> None:
    feature = sa.table("feature", sa.column("title", sa.String()), schema=SCHEMA)
    op.execute(
        insert(feature)
        .values([{"title": title} for title in NEW_FEATURE_TITLES])
        .on_conflict_do_nothing(index_elements=["title"])
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
    # count a guest's uses of one action in the window, find the oldest
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
    # keep the features that threads already use
    op.execute(
        sa.text(
            f"DELETE FROM {SCHEMA}.feature f WHERE f.title = ANY(:titles) "
            f"AND NOT EXISTS (SELECT 1 FROM {SCHEMA}.thread t WHERE t.feature_id = f.id)"
        ).bindparams(titles=NEW_FEATURE_TITLES)
    )
