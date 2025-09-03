"""add created_at / updated_at to planets

Revision ID: 9374509056cb
Revises: abcce1a30e83
Create Date: 2025-09-03 20:58:08.807008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9374509056cb'
down_revision: Union[str, Sequence[str], None] = 'abcce1a30e83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        'planets',
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False)
    )
    op.add_column(
        'planets',
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False)
    )

    op.alter_column('planets', 'created_at', server_default=None)
    op.alter_column('planets', 'updated_at', server_default=None)



def downgrade():
    op.drop_column('planets', 'updated_at')
    op.drop_column('planets', 'created_at')
