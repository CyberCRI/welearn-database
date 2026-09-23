"""keycloack_id_for_user_id

Revision ID: f10903998081
Revises: 5d46d7920342
Create Date: 2026-09-23 14:27:26.389768

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f10903998081"
down_revision: Union[str, None] = "5d46d7920342"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "inferred_user",
        sa.Column("keycloak_id", sa.Uuid(), nullable=True, unique=True),
        schema="user_related",
    )


def downgrade() -> None:
    op.drop_column("inferred_user", "keycloak_id", schema="user_related")
