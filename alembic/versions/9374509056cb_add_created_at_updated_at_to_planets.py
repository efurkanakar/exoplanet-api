"""add created_at / updated_at to planets

Revision ID: 9374509056cb
Revises: abcce1a30e83
Create Date: 2025-09-03 20:58:08.807008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '9374509056cb'
down_revision: Union[str, Sequence[str], None] = 'abcce1a30e83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "planets",
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "planets",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.alter_column("planets", "is_deleted", server_default=None)


def downgrade() -> None:
    op.drop_column("planets", "deleted_at")
    op.drop_column("planets", "is_deleted")