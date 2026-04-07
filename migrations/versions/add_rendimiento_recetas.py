"""Add rendimiento and nota fields to recetas table

Revision ID: add_rendimiento_recetas_001
Revises: 
Create Date: 2026-04-06 18:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_rendimiento_recetas_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add rendimiento column with default 0
    op.add_column('recetas', sa.Column('rendimiento', sa.Float(), nullable=False, server_default='0'))
    
    # Add nota column (optional notes)
    op.add_column('recetas', sa.Column('nota', sa.Text(), nullable=True))


def downgrade():
    # Remove nota column
    op.drop_column('recetas', 'nota')
    
    # Remove rendimiento column
    op.drop_column('recetas', 'rendimiento')
