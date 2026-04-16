"""Backfill articulo_id from producto for mermas legacy rows

Revision ID: b91e4c2d7a6f
Revises: a4d9b3e2f1c7
Create Date: 2026-04-16 13:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b91e4c2d7a6f'
down_revision = 'a4d9b3e2f1c7'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    # Legacy materia-prima rows.
    op.execute(
        sa.text(
            """
            UPDATE mermas
            SET articulo_id = id_materia
            WHERE tipo_articulo = 'MateriaPrima'
              AND articulo_id IS NULL
              AND id_materia IS NOT NULL
            """
        )
    )

    # Legacy inventario rows where only id_producto remains.
    op.execute(
        sa.text(
            """
            UPDATE mermas m
            LEFT JOIN inventario_terminado it ON it.id_producto = m.id_producto
            SET m.articulo_id = COALESCE(m.articulo_id, m.id_inventario, it.id_inventario)
            WHERE m.tipo_articulo = 'InventarioTerminado'
              AND m.articulo_id IS NULL
            """
        )
    )

    nulls = bind.execute(
        sa.text("SELECT COUNT(*) FROM mermas WHERE articulo_id IS NULL")
    ).scalar()

    if not nulls:
        with op.batch_alter_table('mermas', schema=None) as batch_op:
            batch_op.alter_column('articulo_id', existing_type=sa.Integer(), nullable=False)


def downgrade():
    # Data backfill migration: no-op downgrade to avoid lossy rollback.
    pass
