"""add soft delete columns to planets

Revision ID: abcce1a30e83
Revises: 2f6bf5cea480
Create Date: 2025-09-03 15:22:58.116098

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abcce1a30e83'
down_revision: Union[str, Sequence[str], None] = '2f6bf5cea480'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "planets",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.add_column(
        "planets",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.alter_column(
        "planets",
        "created_at",
        server_default=None,
        existing_type=sa.DateTime(timezone=True),
    )
    op.alter_column(
        "planets",
        "updated_at",
        server_default=None,
        existing_type=sa.DateTime(timezone=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("planets", "updated_at")
    op.drop_column("planets", "created_at")
