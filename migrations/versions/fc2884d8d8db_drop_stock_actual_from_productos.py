"""drop stock_actual from productos

Revision ID: fc2884d8d8db
Revises: 70048c8c83c1
Create Date: 2026-04-15 13:07:43.190165

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc2884d8d8db'
down_revision = '70048c8c83c1'
branch_labels = None
depends_on = None


def upgrade():
    if op.get_context().is_offline_mode():
        with op.batch_alter_table("productos", schema=None) as batch_op:
            batch_op.drop_constraint(
                "check_stock_actual_producto_no_negativo",
                type_="check",
            )
            batch_op.drop_column("stock_actual")
        return

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    columnas = {c["name"] for c in inspector.get_columns("productos")}
    checks = {c.get("name") for c in inspector.get_check_constraints("productos")}

    with op.batch_alter_table("productos", schema=None) as batch_op:
        if "check_stock_actual_producto_no_negativo" in checks:
            batch_op.drop_constraint(
                "check_stock_actual_producto_no_negativo",
                type_="check",
            )

        if "stock_actual" in columnas:
            batch_op.drop_column("stock_actual")


def downgrade():
    if op.get_context().is_offline_mode():
        with op.batch_alter_table("productos", schema=None) as batch_op:
            batch_op.add_column(
                sa.Column(
                    "stock_actual",
                    sa.Float(),
                    nullable=False,
                    server_default="0",
                )
            )
            batch_op.create_check_constraint(
                "check_stock_actual_producto_no_negativo",
                "stock_actual >= 0",
            )
        return

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    columnas = {c["name"] for c in inspector.get_columns("productos")}
    checks = {c.get("name") for c in inspector.get_check_constraints("productos")}

    with op.batch_alter_table("productos", schema=None) as batch_op:
        if "stock_actual" not in columnas:
            batch_op.add_column(
                sa.Column(
                    "stock_actual",
                    sa.Float(),
                    nullable=False,
                    server_default="0",
                )
            )

        if "check_stock_actual_producto_no_negativo" not in checks:
            batch_op.create_check_constraint(
                "check_stock_actual_producto_no_negativo",
                "stock_actual >= 0",
            )
