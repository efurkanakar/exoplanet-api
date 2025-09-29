"""add soft delete to planets

Revision ID: 2f6bf5cea480
Revises: 535648a0f9c9
Create Date: 2025-09-03 15:21:24.973269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f6bf5cea480'
down_revision: Union[str, Sequence[str], None] = '535648a0f9c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # No-op: soft-delete columns are added in later revisions; this revision is
    # kept so the migration history remains intact.
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # No-op: nothing to remove because this revision doesn't alter the schema.
    pass
