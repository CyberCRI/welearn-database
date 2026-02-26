"""data collection for focus group

Revision ID: 9b4f1da0c1f2
Revises: 2ad4895b2674
Create Date: 2026-02-23 18:11:55.857517

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "9b4f1da0c1f2"
down_revision: Union[str, None] = "2ad4895b2674"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "chat_message",
        sa.Column(
            "is_retrieved_by_user",
            sa.Boolean(),
            nullable=False,
            default=False,
            server_default="False",
        ),
        schema="user_related",
    )
    op.add_column(
        "chat_message",
        sa.Column("original_feature_name", sa.String(), nullable=True),
        schema="user_related",
    )
    op.create_table(
        "filter_used_in_query",
        sa.Column(
            "id", sa.Uuid(), server_default=sa.func.gen_random_uuid(), nullable=False
        ),
        sa.Column("message_id", sa.Uuid(), nullable=False),
        sa.Column(
            "filter_type",
            postgresql.ENUM(
                "sdg",
                "source",
                name="filter_type",
                schema="user_related",
            ),
            nullable=False,
        ),
        sa.Column("filter_value", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["message_id"],
            ["user_related.chat_message.id"],
            name="filter_used_in_query_message_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="user_related",
    )


def downgrade() -> None:
    op.drop_column("chat_message", "is_retrieved_by_user", schema="user_related")
    op.drop_column("chat_message", "original_feature_name", schema="user_related")
    op.drop_constraint(
        "filter_used_in_query_message_id_fkey",
        "filter_used_in_query",
        schema="user_related",
        type_="foreignkey",
    )
    op.drop_table("filter_used_in_query", schema="user_related")
    op.execute("DROP TYPE IF EXISTS user_related.filter_type")
