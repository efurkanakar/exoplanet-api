"""add is_deleted and deleted_at to planets

Revision ID: 319364dd65e5
Revises: 9374509056cb
Create Date: 2025-09-06 16:30:28.045240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '319364dd65e5'
down_revision: Union[str, Sequence[str], None] = '9374509056cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
