"""Agregar bandera de origen desde produccion en compras

Revision ID: 8b7f1a6c4c2d
Revises: 3d17408121ec
Create Date: 2026-04-08 19:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b7f1a6c4c2d'
down_revision = '3d17408121ec'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('compras', schema=None) as batch_op:
        batch_op.add_column(sa.Column('desde_produccion', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    with op.batch_alter_table('compras', schema=None) as batch_op:
        batch_op.drop_column('desde_produccion')
