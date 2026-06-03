"""add_university_data

Revision ID: 8b780aea403a
Revises: f1ce0ad2845b
Create Date: 2026-06-03 11:34:02.441435

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "8b780aea403a"
down_revision: Union[str, None] = "f1ce0ad2845b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "inferred_user",
        sa.Column("university_title", sa.String(), nullable=True),
        schema="user_related",
    )
    op.add_column(
        "inferred_user",
        sa.Column(
            "role",
            postgresql.ENUM(
                "student",
                "teacher",
                "staff",
                name="university_role",
                schema="user_related",
            ),
            nullable=True,
        ),
        schema="user_related",
    )


def downgrade() -> None:
    op.drop_column("inferred_user", "university_title", schema="user_related")
    op.drop_column("inferred_user", "role", schema="user_related")
    op.execute("DROP TYPE user_related.university_role")
