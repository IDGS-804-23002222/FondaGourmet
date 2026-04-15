"""Frescura productos y merma automatica

Revision ID: 7f3c2d9a1b4e
Revises: e1a4b7c9d2f0
Create Date: 2026-04-14 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f3c2d9a1b4e'
down_revision = 'e1a4b7c9d2f0'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fecha_produccion', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('dias_duracion', sa.Integer(), nullable=False, server_default='2'))
        batch_op.add_column(sa.Column('fecha_merma', sa.DateTime(), nullable=True))
        batch_op.create_check_constraint('check_dias_duracion_producto_minimo', 'dias_duracion >= 2')


def downgrade():
    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.drop_constraint('check_dias_duracion_producto_minimo', type_='check')
        batch_op.drop_column('fecha_merma')
        batch_op.drop_column('dias_duracion')
        batch_op.drop_column('fecha_produccion')
