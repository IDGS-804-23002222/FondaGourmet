"""Agregar estado de pago y flags de detalle a pedidos

Revision ID: f6b0c0d4a123
Revises: e1a4b7c9d2f0
Create Date: 2026-04-14 21:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6b0c0d4a123'
down_revision = 'e1a4b7c9d2f0'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('pedidos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('estado_pago', sa.String(length=50), nullable=False, server_default='Pendiente'))

    with op.batch_alter_table('detalle_pedido', schema=None) as batch_op:
        batch_op.add_column(sa.Column('atendido', sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column('en_produccion', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    with op.batch_alter_table('detalle_pedido', schema=None) as batch_op:
        batch_op.drop_column('en_produccion')
        batch_op.drop_column('atendido')

    with op.batch_alter_table('pedidos', schema=None) as batch_op:
        batch_op.drop_column('estado_pago')
