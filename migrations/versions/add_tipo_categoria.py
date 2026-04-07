"""Add tipo_categoria to categorias table

Revision ID: add_tipo_categoria_001
Revises: 
Create Date: 2026-04-06 18:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_tipo_categoria_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add tipo_categoria column with default 'platillo'
    op.add_column('categorias', sa.Column('tipo_categoria', sa.String(20), nullable=False, server_default='platillo'))
    
    # Create index for tipo_categoria for better query performance
    op.create_index('ix_categorias_tipo_categoria', 'categorias', ['tipo_categoria'])


def downgrade():
    # Drop the index
    op.drop_index('ix_categorias_tipo_categoria', table_name='categorias')
    
    # Remove tipo_categoria column
    op.drop_column('categorias', 'tipo_categoria')
