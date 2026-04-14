#!/usr/bin/env python3
"""Idempotent DB sync for FondaGourmet.

This script aligns an existing MySQL schema with the current app models for:
- categorias_proveedor
- categorias_ingrediente
- categorias_platillo
- proveedores.id_categoria_proveedor
- materias_primas.id_categoria_ingrediente
- productos.id_categoria_platillo

It also keeps legacy columns (id_categoria) nullable so mixed deployments do not fail.
It also ensures recetas.porciones exists and is valid (> 0 at data level).
"""

from sqlalchemy import text

from app import create_app, db


def has_table(session, table_name):
    row = session.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
              AND table_name = :table_name
            """
        ),
        {"table_name": table_name},
    ).scalar()
    return bool(row)


def has_column(session, table_name, column_name):
    row = session.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name = :table_name
              AND column_name = :column_name
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    ).scalar()
    return bool(row)


def is_nullable(session, table_name, column_name):
    row = session.execute(
        text(
            """
            SELECT is_nullable
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name = :table_name
              AND column_name = :column_name
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    ).first()
    return row and row[0] == "YES"


def has_fk(session, table_name, fk_name):
    row = session.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.table_constraints
            WHERE constraint_schema = DATABASE()
              AND table_name = :table_name
              AND constraint_name = :fk_name
              AND constraint_type = 'FOREIGN KEY'
            """
        ),
        {"table_name": table_name, "fk_name": fk_name},
    ).scalar()
    return bool(row)


def has_check_constraint(session, table_name, constraint_name):
    row = session.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.table_constraints
            WHERE constraint_schema = DATABASE()
              AND table_name = :table_name
              AND constraint_name = :constraint_name
              AND constraint_type = 'CHECK'
            """
        ),
        {"table_name": table_name, "constraint_name": constraint_name},
    ).scalar()
    return bool(row)


def run():
    app = create_app()
    with app.app_context():
        s = db.session

        # 1) Category tables
        s.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS categorias_proveedor (
                    id_categoria_proveedor INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL UNIQUE,
                    descripcion TEXT NULL,
                    estado TINYINT(1) DEFAULT 1,
                    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
                """
            )
        )

        s.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS categorias_ingrediente (
                    id_categoria_ingrediente INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL UNIQUE,
                    descripcion TEXT NULL,
                    estado TINYINT(1) DEFAULT 1,
                    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
                """
            )
        )

        s.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS categorias_platillo (
                    id_categoria_platillo INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL UNIQUE,
                    descripcion TEXT NULL,
                    estado TINYINT(1) DEFAULT 1,
                    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
                """
            )
        )

        # 2) Seed catalogs
        for name in ["Verduras", "Lacteos", "Carnes", "Abarrotes", "Bebidas"]:
            s.execute(
                text(
                    "INSERT IGNORE INTO categorias_proveedor (nombre, estado) VALUES (:name, 1)"
                ),
                {"name": name},
            )
            s.execute(
                text(
                    "INSERT IGNORE INTO categorias_ingrediente (nombre, estado) VALUES (:name, 1)"
                ),
                {"name": name},
            )

        for name in ["Entradas", "Platos fuertes", "Postres", "Bebidas"]:
            s.execute(
                text(
                    "INSERT IGNORE INTO categorias_platillo (nombre, estado) VALUES (:name, 1)"
                ),
                {"name": name},
            )

        # 3) Add columns when missing
        if has_table(s, "proveedores") and not has_column(s, "proveedores", "id_categoria_proveedor"):
            s.execute(text("ALTER TABLE proveedores ADD COLUMN id_categoria_proveedor INT NULL"))

        if has_table(s, "materias_primas") and not has_column(s, "materias_primas", "id_categoria_ingrediente"):
            s.execute(text("ALTER TABLE materias_primas ADD COLUMN id_categoria_ingrediente INT NULL"))

        if has_table(s, "productos") and not has_column(s, "productos", "id_categoria_platillo"):
            s.execute(text("ALTER TABLE productos ADD COLUMN id_categoria_platillo INT NULL"))

        # Recetas: ensure porciones exists for compatibility with current models
        if has_table(s, "recetas"):
            if not has_column(s, "recetas", "porciones"):
                s.execute(text("ALTER TABLE recetas ADD COLUMN porciones INT NOT NULL DEFAULT 1"))
            else:
                # Normalize data first so the NOT NULL/default alteration can be applied safely.
                s.execute(text("UPDATE recetas SET porciones = 1 WHERE porciones IS NULL OR porciones <= 0"))
                s.execute(text("ALTER TABLE recetas MODIFY COLUMN porciones INT NOT NULL DEFAULT 1"))

            if not has_check_constraint(s, "recetas", "check_receta_porciones_positivas"):
                s.execute(
                    text(
                        """
                        ALTER TABLE recetas
                        ADD CONSTRAINT check_receta_porciones_positivas
                        CHECK (porciones > 0)
                        """
                    )
                )

        # 4) Keep legacy id_categoria nullable (avoids insert crashes in mixed environments)
        if has_column(s, "materias_primas", "id_categoria") and not is_nullable(s, "materias_primas", "id_categoria"):
            s.execute(text("ALTER TABLE materias_primas MODIFY COLUMN id_categoria INT NULL"))

        if has_column(s, "productos", "id_categoria") and not is_nullable(s, "productos", "id_categoria"):
            s.execute(text("ALTER TABLE productos MODIFY COLUMN id_categoria INT NULL"))

        # 5) Backfill new FKs from previous categoria mapping
        if has_column(s, "proveedores", "id_categoria_proveedor"):
            s.execute(
                text(
                    """
                    UPDATE proveedores
                    SET id_categoria_proveedor = COALESCE(
                        id_categoria_proveedor,
                        (SELECT id_categoria_proveedor
                         FROM categorias_proveedor
                         WHERE nombre = 'Abarrotes'
                         LIMIT 1)
                    )
                    """
                )
            )

        if has_column(s, "materias_primas", "id_categoria_ingrediente"):
            if has_column(s, "materias_primas", "id_categoria"):
                s.execute(
                    text(
                        """
                        UPDATE materias_primas mp
                        LEFT JOIN categorias c ON c.id_categoria = mp.id_categoria
                        LEFT JOIN categorias_ingrediente ci ON LOWER(ci.nombre) = LOWER(c.nombre)
                        SET mp.id_categoria_ingrediente = COALESCE(
                            mp.id_categoria_ingrediente,
                            ci.id_categoria_ingrediente,
                            (SELECT id_categoria_ingrediente
                             FROM categorias_ingrediente
                             WHERE nombre = 'Abarrotes'
                             LIMIT 1)
                        )
                        """
                    )
                )
            else:
                s.execute(
                    text(
                        """
                        UPDATE materias_primas
                        SET id_categoria_ingrediente = COALESCE(
                            id_categoria_ingrediente,
                            (SELECT id_categoria_ingrediente
                             FROM categorias_ingrediente
                             WHERE nombre = 'Abarrotes'
                             LIMIT 1)
                        )
                        """
                    )
                )

        if has_column(s, "productos", "id_categoria_platillo"):
            if has_column(s, "productos", "id_categoria"):
                s.execute(
                    text(
                        """
                        UPDATE productos p
                        LEFT JOIN categorias c ON c.id_categoria = p.id_categoria
                        LEFT JOIN categorias_platillo cp ON LOWER(cp.nombre) = LOWER(c.nombre)
                        SET p.id_categoria_platillo = COALESCE(
                            p.id_categoria_platillo,
                            cp.id_categoria_platillo,
                            (SELECT id_categoria_platillo
                             FROM categorias_platillo
                             WHERE nombre = 'Platos fuertes'
                             LIMIT 1)
                        )
                        """
                    )
                )
            else:
                s.execute(
                    text(
                        """
                        UPDATE productos
                        SET id_categoria_platillo = COALESCE(
                            id_categoria_platillo,
                            (SELECT id_categoria_platillo
                             FROM categorias_platillo
                             WHERE nombre = 'Platos fuertes'
                             LIMIT 1)
                        )
                        """
                    )
                )

        # 6) Add FK constraints when missing
        if has_column(s, "proveedores", "id_categoria_proveedor") and not has_fk(
            s, "proveedores", "fk_proveedores_categoria_proveedor"
        ):
            s.execute(
                text(
                    """
                    ALTER TABLE proveedores
                    ADD CONSTRAINT fk_proveedores_categoria_proveedor
                    FOREIGN KEY (id_categoria_proveedor)
                    REFERENCES categorias_proveedor (id_categoria_proveedor)
                    """
                )
            )

        if has_column(s, "materias_primas", "id_categoria_ingrediente") and not has_fk(
            s, "materias_primas", "fk_materias_primas_categoria_ingrediente"
        ):
            s.execute(
                text(
                    """
                    ALTER TABLE materias_primas
                    ADD CONSTRAINT fk_materias_primas_categoria_ingrediente
                    FOREIGN KEY (id_categoria_ingrediente)
                    REFERENCES categorias_ingrediente (id_categoria_ingrediente)
                    """
                )
            )

        if has_column(s, "productos", "id_categoria_platillo") and not has_fk(
            s, "productos", "fk_productos_categoria_platillo"
        ):
            s.execute(
                text(
                    """
                    ALTER TABLE productos
                    ADD CONSTRAINT fk_productos_categoria_platillo
                    FOREIGN KEY (id_categoria_platillo)
                    REFERENCES categorias_platillo (id_categoria_platillo)
                    """
                )
            )

        s.commit()
        print("DB sync completed successfully.")


if __name__ == "__main__":
    run()
