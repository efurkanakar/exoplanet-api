"""baseline

Revision ID: 535648a0f9c9
Revises: 
Create Date: 2025-09-xx xx:xx:xx

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "535648a0f9c9"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "planets",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("disc_method", sa.String(), nullable=False),
        sa.Column("disc_year", sa.Integer(), nullable=False),
        sa.Column("orbperd", sa.Float(), nullable=False),
        sa.Column("rade", sa.Float(), nullable=False),
        sa.Column("masse", sa.Float(), nullable=False),
        sa.Column("st_teff", sa.Float(), nullable=False),
        sa.Column("st_rad", sa.Float(), nullable=False),
        sa.Column("st_mass", sa.Float(), nullable=False),
    )

    # index
    op.create_index("ix_planets_id", "planets", ["id"])
    op.create_index("ix_planets_disc_method", "planets", ["disc_method"])
    op.create_index("ix_planets_disc_year", "planets", ["disc_year"])
    op.create_index("ix_planets_name", "planets", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_planets_name", table_name="planets")
    op.drop_index("ix_planets_disc_year", table_name="planets")
    op.drop_index("ix_planets_disc_method", table_name="planets")
    op.drop_index("ix_planets_id", table_name="planets")
    op.drop_table("planets")
