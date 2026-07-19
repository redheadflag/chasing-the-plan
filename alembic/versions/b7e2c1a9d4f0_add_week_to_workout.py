"""add week to workout

Revision ID: b7e2c1a9d4f0
Revises: 26521705c208
Create Date: 2026-07-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7e2c1a9d4f0'
down_revision: Union[str, Sequence[str], None] = '26521705c208'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the per-workout week number.

    NOT NULL with server_default='1' so every existing workout is backfilled to
    week 1 (the default mesocycle) as the column is created.
    """
    op.add_column(
        'workout',
        sa.Column('week', sa.Integer(), nullable=False, server_default='1'),
    )
    op.create_index(op.f('ix_workout_week'), 'workout', ['week'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_workout_week'), table_name='workout')
    op.drop_column('workout', 'week')
