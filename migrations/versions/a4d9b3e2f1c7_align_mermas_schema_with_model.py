"""Align mermas schema with current ORM model

Revision ID: a4d9b3e2f1c7
Revises: fc2884d8d8db
Create Date: 2026-04-16 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4d9b3e2f1c7'
down_revision = 'fc2884d8d8db'
branch_labels = None
depends_on = None


def _get_columns(inspector, table_name):
    return {c['name'] for c in inspector.get_columns(table_name)}


def _drop_legacy_motivo_checks(inspector):
    checks = inspector.get_check_constraints('mermas')
    check_names = {c.get('name') for c in checks if c.get('name')}
    legacy_names = {
        'check_merma_motivo',
        'ck_mermas_motivo',
        'mermas_chk_1',
    }

    for check_name in sorted(check_names.intersection(legacy_names)):
        with op.batch_alter_table('mermas', schema=None) as batch_op:
            batch_op.drop_constraint(check_name, type_='check')


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = _get_columns(inspector, 'mermas')

    with op.batch_alter_table('mermas', schema=None) as batch_op:
        if 'tipo_articulo' not in columns:
            batch_op.add_column(sa.Column('tipo_articulo', sa.String(length=50), nullable=True))
        if 'articulo_id' not in columns:
            batch_op.add_column(sa.Column('articulo_id', sa.Integer(), nullable=True))
        if 'fecha_registro' not in columns:
            batch_op.add_column(sa.Column('fecha_registro', sa.DateTime(), nullable=True))
        if 'usuario_id' not in columns:
            batch_op.add_column(sa.Column('usuario_id', sa.Integer(), nullable=True))

    inspector = sa.inspect(bind)
    columns = _get_columns(inspector, 'mermas')

    if 'tipo_articulo' in columns:
        if 'tipo_origen' in columns:
            op.execute(
                sa.text(
                    """
                    UPDATE mermas
                    SET tipo_articulo = COALESCE(tipo_articulo, tipo_origen)
                    """
                )
            )
        if 'id_materia' in columns:
            op.execute(
                sa.text(
                    """
                    UPDATE mermas
                    SET tipo_articulo = 'MateriaPrima'
                    WHERE tipo_articulo IS NULL AND id_materia IS NOT NULL
                    """
                )
            )
        if 'id_inventario' in columns:
            op.execute(
                sa.text(
                    """
                    UPDATE mermas
                    SET tipo_articulo = 'InventarioTerminado'
                    WHERE tipo_articulo IS NULL AND id_inventario IS NOT NULL
                    """
                )
            )

    if 'articulo_id' in columns:
        if 'id_materia' in columns:
            op.execute(
                sa.text(
                    """
                    UPDATE mermas
                    SET articulo_id = id_materia
                    WHERE articulo_id IS NULL AND id_materia IS NOT NULL
                    """
                )
            )
        if 'id_inventario' in columns:
            op.execute(
                sa.text(
                    """
                    UPDATE mermas
                    SET articulo_id = id_inventario
                    WHERE articulo_id IS NULL AND id_inventario IS NOT NULL
                    """
                )
            )

    if 'fecha_registro' in columns:
        if 'fecha' in columns:
            op.execute(
                sa.text(
                    """
                    UPDATE mermas
                    SET fecha_registro = COALESCE(fecha_registro, fecha)
                    """
                )
            )
        op.execute(
            sa.text(
                """
                UPDATE mermas
                SET fecha_registro = COALESCE(fecha_registro, NOW())
                """
            )
        )

    if 'usuario_id' in columns and 'id_usuario_registro' in columns:
        op.execute(
            sa.text(
                """
                UPDATE mermas
                SET usuario_id = COALESCE(usuario_id, id_usuario_registro)
                """
            )
        )

    if 'motivo' in columns:
        _drop_legacy_motivo_checks(inspector)
        op.execute(sa.text("UPDATE mermas SET motivo = 'Caducidad' WHERE motivo IN ('Caducado')"))
        op.execute(sa.text("UPDATE mermas SET motivo = 'Daño' WHERE motivo IN ('Danado', 'Dañado')"))
        op.execute(
            sa.text(
                """
                UPDATE mermas
                SET motivo = 'Error de Producción'
                WHERE motivo IN ('Error de Produccion')
                """
            )
        )
        op.execute(sa.text("UPDATE mermas SET motivo = 'Otro' WHERE motivo IS NULL OR TRIM(motivo) = ''"))

    nulls = bind.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM mermas
            WHERE tipo_articulo IS NULL
               OR articulo_id IS NULL
               OR fecha_registro IS NULL
               OR usuario_id IS NULL
            """
        )
    ).scalar()

    if not nulls:
        with op.batch_alter_table('mermas', schema=None) as batch_op:
            batch_op.alter_column('tipo_articulo', existing_type=sa.String(length=50), nullable=False)
            batch_op.alter_column('articulo_id', existing_type=sa.Integer(), nullable=False)
            batch_op.alter_column('fecha_registro', existing_type=sa.DateTime(), nullable=False)
            batch_op.alter_column('usuario_id', existing_type=sa.Integer(), nullable=False)


def downgrade():
    # No eliminamos columnas para evitar perdida de datos en despliegues existentes.
    pass
