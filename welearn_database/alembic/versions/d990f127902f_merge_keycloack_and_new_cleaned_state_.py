"""merge keycloack and new cleaned state related stuff

Revision ID: d990f127902f
Revises: 0310ff0bda4f, f10903998081
Create Date: 2026-09-23 16:20:59.738749

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd990f127902f'
down_revision: Union[str, None] = ('0310ff0bda4f', 'f10903998081')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
