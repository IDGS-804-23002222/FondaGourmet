"""Relax legacy required columns in mermas for ORM compatibility

Revision ID: e4f9c2a1b7d3
Revises: d27f6b1e8a9c
Create Date: 2026-04-16 16:24:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4f9c2a1b7d3'
down_revision = 'd27f6b1e8a9c'
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
    table_names = inspector.get_table_names(schema=None)
    if 'mermas' not in table_names:
        return

    columns = _get_columns(inspector, 'mermas')

    if 'costo_unitario' in columns:
        op.execute(
            sa.text(
                """
                UPDATE mermas
                SET costo_unitario = COALESCE(
                    costo_unitario,
                    CASE
                        WHEN cantidad IS NOT NULL AND cantidad <> 0 THEN (costo_perdida / cantidad)
                        ELSE 0
                    END
                )
                """
            )
        )
        if _is_nullable(inspector, 'mermas', 'costo_unitario') is False:
            with op.batch_alter_table('mermas', schema=None) as batch_op:
                batch_op.alter_column(
                    'costo_unitario',
                    existing_type=sa.Float(),
                    nullable=True,
                )

    if 'id_usuario_registro' in columns and 'usuario_id' in columns:
        op.execute(
            sa.text(
                """
                UPDATE mermas
                SET id_usuario_registro = COALESCE(id_usuario_registro, usuario_id)
                WHERE usuario_id IS NOT NULL
                """
            )
        )
        if _is_nullable(inspector, 'mermas', 'id_usuario_registro') is False:
            with op.batch_alter_table('mermas', schema=None) as batch_op:
                batch_op.alter_column(
                    'id_usuario_registro',
                    existing_type=sa.Integer(),
                    nullable=True,
                )

    if 'id_usuario_autorizacion' in columns and _is_nullable(inspector, 'mermas', 'id_usuario_autorizacion') is False:
        with op.batch_alter_table('mermas', schema=None) as batch_op:
            batch_op.alter_column(
                'id_usuario_autorizacion',
                existing_type=sa.Integer(),
                nullable=True,
            )

    if 'autorizada' in columns and _is_nullable(inspector, 'mermas', 'autorizada') is False:
        with op.batch_alter_table('mermas', schema=None) as batch_op:
            batch_op.alter_column(
                'autorizada',
                existing_type=sa.Boolean(),
                nullable=True,
            )

    if 'fecha' in columns and 'fecha_registro' in columns:
        op.execute(
            sa.text(
                """
                UPDATE mermas
                SET fecha = COALESCE(fecha, fecha_registro)
                WHERE fecha_registro IS NOT NULL
                """
            )
        )
        if _is_nullable(inspector, 'mermas', 'fecha') is False:
            with op.batch_alter_table('mermas', schema=None) as batch_op:
                batch_op.alter_column(
                    'fecha',
                    existing_type=sa.DateTime(),
                    nullable=True,
                )


def downgrade():
    # Keep columns nullable in downgrade to avoid reintroducing runtime insert failures.
    pass
