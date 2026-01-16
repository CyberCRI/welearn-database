"""data collection

Revision ID: 2ad4895b2674
Revises: 068312e7800c
Create Date: 2026-01-16 15:55:41.447852

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "2ad4895b2674"
down_revision: Union[str, None] = "068312e7800c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "data_collection_campaign_management",
        sa.Column(
            "id", sa.Uuid(), server_default=sa.func.gen_random_uuid(), nullable=False
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("end_at", postgresql.TIMESTAMP(), nullable=False),
        sa.Column(
            "created_at", postgresql.TIMESTAMP(), server_default="NOW()", nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="user_related",
    )

    op.add_column(
        "chat_message",
        sa.Column("role", sa.String(), nullable=False),
        schema="user_related",
    )
    op.add_column(
        "chat_message",
        sa.Column("inferred_user_id", sa.Uuid(), nullable=False),
        schema="user_related",
    )
    op.add_column(
        "chat_message",
        sa.Column("conversation_id", sa.Uuid(), nullable=False),
        schema="user_related",
    )
    op.drop_constraint(
        op.f("message_user_id_fkey"),
        "chat_message",
        schema="user_related",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "message_inferred_user_id_fkey",
        "chat_message",
        "inferred_user",
        ["inferred_user_id"],
        ["id"],
        source_schema="user_related",
        referent_schema="user_related",
    )
    op.drop_column("chat_message", "user_id", schema="user_related")
    op.add_column(
        "returned_document",
        sa.Column("is_clicked", sa.Boolean(), nullable=False),
        schema="user_related",
    )


def downgrade() -> None:
    op.drop_column("returned_document", "is_clicked", schema="user_related")
    op.add_column(
        "chat_message",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        schema="user_related",
    )
    op.drop_constraint(
        "message_inferred_user_id_fkey",
        "chat_message",
        schema="user_related",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("message_user_id_fkey"),
        "chat_message",
        "user_profile",
        ["user_id"],
        ["id"],
        source_schema="user_related",
        referent_schema="user_related",
    )
    op.drop_column("chat_message", "conversation_id", schema="user_related")
    op.drop_column("chat_message", "inferred_user_id", schema="user_related")
    op.drop_column("chat_message", "role", schema="user_related")
    op.drop_table("data_collection_campaign_management", schema="user_related")
