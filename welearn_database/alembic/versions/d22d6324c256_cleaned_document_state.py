"""cleaned_document_state

Revision ID: d22d6324c256
Revises: 5d46d7920342
Create Date: 2026-09-23 11:18:46.784209

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from welearn_database.data.enumeration import Step

# revision identifiers, used by Alembic.
revision: str = "d22d6324c256"
down_revision: Union[str, None] = "5d46d7920342"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        f"""ALTER TYPE document_related.step ADD VALUE '{Step.DOCUMENT_CLEANED.value}'"""
    )


def downgrade() -> None:
    pass
