"""add analytic form

Revision ID: f5e91a5c950d
Revises: 6d4346fad6f4
Create Date: 2026-09-02 16:32:55.188400

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f5e91a5c950d"
down_revision: Union[str, None] = "6d4346fad6f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "analytic_form",
        sa.Column(
            "id", sa.Uuid(), server_default=sa.func.gen_random_uuid(), nullable=False
        ),
        sa.Column("form_name", sa.String(), nullable=False),
        sa.Column("question", sa.String(), nullable=False),
        sa.Column("answer", sa.String(), nullable=False),
        sa.Column(
            "answer_type",
            postgresql.ENUM(
                "text",
                "checkbox",
                "predefined_text",
                name="answer_type",
                schema="user_related",
            ),
            nullable=False,
        ),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=False),
            nullable=False,
            server_default="NOW()",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["user_related.session.id"],
            name="analytic_form_session_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="user_related",
    )


def downgrade() -> None:
    op.drop_constraint(
        "analytic_form_session_id_fkey",
        "analytic_form",
        schema="user_related",
        type_="foreignkey",
    )
    op.drop_table("analytic_form", schema="user_related")
    op.execute("DROP TYPE IF EXISTS user_related.answer_type")
