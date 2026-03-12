"""update session view

Revision ID: f8602200fa99
Revises: 9b4f1da0c1f2
Create Date: 2026-03-12 12:34:29.240684

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f8602200fa99"
down_revision: Union[str, None] = "9b4f1da0c1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
CREATE OR REPLACE VIEW grafana."session"
AS SELECT *
   FROM user_related.session;
    """
    )


def downgrade() -> None:
    op.execute(
        """
CREATE OR REPLACE VIEW grafana."session"
AS SELECT session.id,
    session.inferred_user_id,
    session.created_at,
    session.end_at,
    session.host
   FROM user_related.session;
    """
    )
