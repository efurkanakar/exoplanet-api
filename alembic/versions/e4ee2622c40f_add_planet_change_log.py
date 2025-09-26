"""add planet change log

Revision ID: e4ee2622c40f
Revises: 319364dd65e5
Create Date: 2025-09-26 22:37:21.434494

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e4ee2622c40f"
down_revision: Union[str, Sequence[str], None] = "319364dd65e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create table for planet change logs."""
    op.create_table(
        "planet_change_logs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("planet_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=20), nullable=False),
        sa.Column("changes", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["planet_id"], ["planets.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_planet_change_logs_planet_id",
        "planet_change_logs",
        ["planet_id"],
    )
    op.create_index(
        "ix_planet_change_logs_created_at",
        "planet_change_logs",
        ["created_at"],
    )


def downgrade() -> None:
    """Drop planet change log table."""
    op.drop_index("ix_planet_change_logs_created_at", table_name="planet_change_logs")
    op.drop_index("ix_planet_change_logs_planet_id", table_name="planet_change_logs")
    op.drop_table("planet_change_logs")
