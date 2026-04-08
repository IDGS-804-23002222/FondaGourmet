"""Separar categorias para proveedor, ingrediente y platillo

Revision ID: b9f4d1e2c3a0
Revises: 66f0d2929165
Create Date: 2026-04-07 18:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9f4d1e2c3a0'
down_revision = '66f0d2929165'
branch_labels = None
depends_on = None


def _seed_catalogos():
    categorias_proveedor = [
        'Verduras',
        'Lacteos',
        'Carnes',
        'Abarrotes',
        'Bebidas',
    ]

    categorias_ingrediente = [
        'Verduras',
        'Lacteos',
        'Carnes',
        'Abarrotes',
        'Bebidas',
    ]

    categorias_platillo = [
        'Entradas',
        'Platos fuertes',
        'Postres',
        'Bebidas',
    ]

    for nombre in categorias_proveedor:
        op.execute(sa.text(
            "INSERT INTO categorias_proveedor (nombre, estado, fecha_creacion) "
            "SELECT :nombre, 1, CURRENT_TIMESTAMP "
            "WHERE NOT EXISTS (SELECT 1 FROM categorias_proveedor WHERE nombre = :nombre)"
        ).bindparams(nombre=nombre))

    for nombre in categorias_ingrediente:
        op.execute(sa.text(
            "INSERT INTO categorias_ingrediente (nombre, estado, fecha_creacion) "
            "SELECT :nombre, 1, CURRENT_TIMESTAMP "
            "WHERE NOT EXISTS (SELECT 1 FROM categorias_ingrediente WHERE nombre = :nombre)"
        ).bindparams(nombre=nombre))

    for nombre in categorias_platillo:
        op.execute(sa.text(
            "INSERT INTO categorias_platillo (nombre, estado, fecha_creacion) "
            "SELECT :nombre, 1, CURRENT_TIMESTAMP "
            "WHERE NOT EXISTS (SELECT 1 FROM categorias_platillo WHERE nombre = :nombre)"
        ).bindparams(nombre=nombre))


def upgrade():
    op.create_table(
        'categorias_proveedor',
        sa.Column('id_categoria_proveedor', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('estado', sa.Boolean(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id_categoria_proveedor'),
        sa.UniqueConstraint('nombre')
    )

    op.create_table(
        'categorias_ingrediente',
        sa.Column('id_categoria_ingrediente', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('estado', sa.Boolean(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id_categoria_ingrediente'),
        sa.UniqueConstraint('nombre')
    )

    op.create_table(
        'categorias_platillo',
        sa.Column('id_categoria_platillo', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('estado', sa.Boolean(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id_categoria_platillo'),
        sa.UniqueConstraint('nombre')
    )

    _seed_catalogos()

    with op.batch_alter_table('proveedores', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id_categoria_proveedor', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_proveedores_categoria_proveedor',
            'categorias_proveedor',
            ['id_categoria_proveedor'],
            ['id_categoria_proveedor']
        )

    with op.batch_alter_table('materias_primas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id_categoria_ingrediente', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_materias_primas_categoria_ingrediente',
            'categorias_ingrediente',
            ['id_categoria_ingrediente'],
            ['id_categoria_ingrediente']
        )

    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id_categoria_platillo', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_productos_categoria_platillo',
            'categorias_platillo',
            ['id_categoria_platillo'],
            ['id_categoria_platillo']
        )

    op.execute(
        """
        UPDATE proveedores
        SET id_categoria_proveedor = (
            SELECT id_categoria_proveedor
            FROM categorias_proveedor
            WHERE nombre = 'Abarrotes'
            LIMIT 1
        )
        WHERE id_categoria_proveedor IS NULL
        """
    )

    op.execute(
        """
        UPDATE materias_primas mp
        LEFT JOIN categorias c ON c.id_categoria = mp.id_categoria
        LEFT JOIN categorias_ingrediente ci ON LOWER(ci.nombre) = LOWER(c.nombre)
        SET mp.id_categoria_ingrediente = COALESCE(
            ci.id_categoria_ingrediente,
            (SELECT id_categoria_ingrediente FROM categorias_ingrediente WHERE nombre = 'Abarrotes' LIMIT 1)
        )
        WHERE mp.id_categoria_ingrediente IS NULL
        """
    )

    op.execute(
        """
        UPDATE productos p
        LEFT JOIN categorias c ON c.id_categoria = p.id_categoria
        LEFT JOIN categorias_platillo cp ON LOWER(cp.nombre) = LOWER(c.nombre)
        SET p.id_categoria_platillo = COALESCE(
            cp.id_categoria_platillo,
            (SELECT id_categoria_platillo FROM categorias_platillo WHERE nombre = 'Platos fuertes' LIMIT 1)
        )
        WHERE p.id_categoria_platillo IS NULL
        """
    )

    with op.batch_alter_table('proveedores', schema=None) as batch_op:
        batch_op.alter_column('id_categoria_proveedor', existing_type=sa.Integer(), nullable=False)

    with op.batch_alter_table('materias_primas', schema=None) as batch_op:
        batch_op.alter_column('id_categoria_ingrediente', existing_type=sa.Integer(), nullable=False)

    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.alter_column('id_categoria_platillo', existing_type=sa.Integer(), nullable=False)


def downgrade():
    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.drop_constraint('fk_productos_categoria_platillo', type_='foreignkey')
        batch_op.drop_column('id_categoria_platillo')

    with op.batch_alter_table('materias_primas', schema=None) as batch_op:
        batch_op.drop_constraint('fk_materias_primas_categoria_ingrediente', type_='foreignkey')
        batch_op.drop_column('id_categoria_ingrediente')

    with op.batch_alter_table('proveedores', schema=None) as batch_op:
        batch_op.drop_constraint('fk_proveedores_categoria_proveedor', type_='foreignkey')
        batch_op.drop_column('id_categoria_proveedor')

    op.drop_table('categorias_platillo')
    op.drop_table('categorias_ingrediente')
    op.drop_table('categorias_proveedor')
