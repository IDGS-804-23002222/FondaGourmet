"""Agregar porciones a recetas

Revision ID: e1a4b7c9d2f0
Revises: 8b7f1a6c4c2d
Create Date: 2026-04-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1a4b7c9d2f0'
down_revision = '8b7f1a6c4c2d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('recetas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('porciones', sa.Integer(), nullable=False, server_default='1'))
        batch_op.create_check_constraint('check_receta_porciones_positivas', 'porciones > 0')


def downgrade():
    with op.batch_alter_table('recetas', schema=None) as batch_op:
        batch_op.drop_constraint('check_receta_porciones_positivas', type_='check')
        batch_op.drop_column('porciones')
