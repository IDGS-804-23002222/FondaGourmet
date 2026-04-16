"""Make mermas.tipo_origen nullable for mixed-schema compatibility

Revision ID: d27f6b1e8a9c
Revises: b91e4c2d7a6f
Create Date: 2026-04-16 16:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd27f6b1e8a9c'
down_revision = 'b91e4c2d7a6f'
branch_labels = None
depends_on = None


def _get_columns(inspector, table_name):
    return {c['name'] for c in inspector.get_columns(table_name)}


def _is_nullable(inspector, table_name, column_name):
    for col in inspector.get_columns(table_name):
        if col.get('name') == column_name:
            return bool(col.get('nullable'))
    return None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = _get_columns(inspector, 'mermas')

    if 'tipo_origen' not in columns:
        return

    if 'tipo_articulo' in columns:
        op.execute(
            sa.text(
                """
                UPDATE mermas
                SET tipo_origen = COALESCE(tipo_origen, tipo_articulo)
                WHERE tipo_articulo IS NOT NULL
                """
            )
        )

    is_nullable = _is_nullable(inspector, 'mermas', 'tipo_origen')
    if is_nullable is False:
        with op.batch_alter_table('mermas', schema=None) as batch_op:
            batch_op.alter_column(
                'tipo_origen',
                existing_type=sa.String(length=30),
                nullable=True,
            )


def downgrade():
    # Keep nullable to avoid reintroducing insert failures in mixed deployments.
    pass
