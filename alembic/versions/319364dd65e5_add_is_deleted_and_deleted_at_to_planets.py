"""add is_deleted and deleted_at to planets

Revision ID: 319364dd65e5
Revises: 9374509056cb
Create Date: 2025-09-06 16:30:28.045240
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "319364dd65e5"
down_revision: Union[str, Sequence[str], None] = "9374509056cb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add soft-delete columns if they don't exist."""
    op.execute(
        """
        DO $$
        BEGIN
            -- is_deleted yoksa ekle (NOT NULL + DEFAULT false), sonra default'u kaldır
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'planets' AND column_name = 'is_deleted'
            ) THEN
                ALTER TABLE planets
                    ADD COLUMN is_deleted boolean NOT NULL DEFAULT false;
                ALTER TABLE planets
                    ALTER COLUMN is_deleted DROP DEFAULT;
            END IF;

            -- deleted_at yoksa ekle
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'planets' AND column_name = 'deleted_at'
            ) THEN
                ALTER TABLE planets
                    ADD COLUMN deleted_at timestamptz NULL;
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    """Downgrade schema: drop columns if they exist."""
    op.execute(
        """
        ALTER TABLE planets
            DROP COLUMN IF EXISTS deleted_at,
            DROP COLUMN IF EXISTS is_deleted;
        """
    )

