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
It also recreates auth-related stored procedures to match the current schema.
It also ensures product freshness fields exist for automatic waste policy.
It also applies SQL DDL scripts in scripts/ for caja compatibility.
It also applies recetas/inventario terminado compatibility SQL scripts.
It also applies compras/proveedores robust compatibility SQL scripts.
It also applies mermas/ajustes compatibility SQL scripts.
"""

from pathlib import Path

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


def has_base_table(session, table_name):
    row = session.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
              AND table_name = :table_name
              AND table_type = 'BASE TABLE'
            """
        ),
        {"table_name": table_name},
    ).scalar()
    return bool(row)


def parse_sql_statements(script_text):
    """Split a SQL script into statements, ignoring semicolons inside quoted strings."""
    filtered_lines = []
    for raw_line in script_text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        filtered_lines.append(raw_line)

    sql = "\n".join(filtered_lines)
    statements = []
    buffer = []
    in_single = False
    in_double = False
    in_backtick = False
    prev = ""

    for ch in sql:
        if ch == "'" and not in_double and not in_backtick and prev != "\\":
            in_single = not in_single
        elif ch == '"' and not in_single and not in_backtick and prev != "\\":
            in_double = not in_double
        elif ch == "`" and not in_single and not in_double:
            in_backtick = not in_backtick

        if ch == ";" and not in_single and not in_double and not in_backtick:
            statement = "".join(buffer).strip()
            if statement:
                statements.append(statement)
            buffer = []
        else:
            buffer.append(ch)

        prev = ch

    tail = "".join(buffer).strip()
    if tail:
        statements.append(tail)

    return statements


def apply_sql_file(session, sql_file_path):
    if not sql_file_path.exists():
        print(f"SQL script not found, skipping: {sql_file_path}")
        return

    script_text = sql_file_path.read_text(encoding="utf-8")
    statements = parse_sql_statements(script_text)

    applied = 0
    skipped = 0
    for stmt in statements:
        normalized = " ".join(stmt.strip().split())
        upper = normalized.upper()

        # Keep transaction ownership in SQLAlchemy session.
        if upper in {"START TRANSACTION", "COMMIT", "ROLLBACK"}:
            skipped += 1
            continue

        # If legacy table objects already exist, skip compatibility views.
        if upper.startswith("CREATE OR REPLACE VIEW CAJA AS") and has_base_table(session, "caja"):
            skipped += 1
            continue
        if upper.startswith("CREATE OR REPLACE VIEW MOVIMIENTOS_CAJA AS") and has_base_table(session, "movimientos_caja"):
            skipped += 1
            continue

        session.execute(text(stmt))
        applied += 1

    print(f"Applied SQL script: {sql_file_path.name} (applied={applied}, skipped={skipped})")


def run():
    app = create_app()
    with app.app_context():
        s = db.session
        scripts_dir = Path(__file__).resolve().parent

        # 0) Apply SQL schema scripts requested for caja/movimientos compatibility.
        apply_sql_file(s, scripts_dir / "schema_caja_sesiones_movimientos.sql")
        apply_sql_file(s, scripts_dir / "schema_recetas_inventario_terminado.sql")
        apply_sql_file(s, scripts_dir / "schema_compras_proveedores_robusto.sql")
        apply_sql_file(s, scripts_dir / "schema_mermas_ajustes.sql")

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

        if has_table(s, "productos") and not has_column(s, "productos", "fecha_produccion"):
            s.execute(text("ALTER TABLE productos ADD COLUMN fecha_produccion DATETIME NULL"))

        if has_table(s, "productos") and not has_column(s, "productos", "dias_duracion"):
            s.execute(text("ALTER TABLE productos ADD COLUMN dias_duracion INT NOT NULL DEFAULT 2"))

        if has_table(s, "productos") and not has_column(s, "productos", "fecha_merma"):
            s.execute(text("ALTER TABLE productos ADD COLUMN fecha_merma DATETIME NULL"))

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

        if has_column(s, "productos", "dias_duracion"):
            s.execute(text("UPDATE productos SET dias_duracion = 2 WHERE dias_duracion IS NULL OR dias_duracion < 2"))

        if has_column(s, "productos", "fecha_produccion") and has_column(s, "productos", "stock_actual"):
            s.execute(text("UPDATE productos SET fecha_produccion = COALESCE(fecha_produccion, fecha_creacion) WHERE stock_actual > 0"))

        if (
            has_column(s, "productos", "fecha_produccion")
            and has_column(s, "productos", "fecha_merma")
            and has_column(s, "productos", "stock_actual")
        ):
            s.execute(
                text(
                    """
                    UPDATE productos
                    SET stock_actual = 0,
                        fecha_merma = COALESCE(fecha_merma, NOW())
                    WHERE stock_actual > 0
                      AND fecha_produccion IS NOT NULL
                      AND fecha_produccion < DATE_SUB(NOW(), INTERVAL 3 DAY)
                    """
                )
            )

        # 6) Mermas compatibility for mixed legacy/new schemas.
        if has_table(s, "mermas"):
            if has_column(s, "mermas", "tipo_articulo") and has_column(s, "mermas", "tipo_origen"):
                s.execute(
                    text(
                        """
                        UPDATE mermas
                        SET tipo_origen = COALESCE(tipo_origen, tipo_articulo)
                        WHERE tipo_articulo IS NOT NULL
                        """
                    )
                )

            # Legacy NOT NULL on tipo_origen breaks ORM inserts that only send tipo_articulo.
            if has_column(s, "mermas", "tipo_origen") and not is_nullable(s, "mermas", "tipo_origen"):
                s.execute(text("ALTER TABLE mermas MODIFY COLUMN tipo_origen VARCHAR(30) NULL"))

            if has_column(s, "mermas", "costo_unitario"):
                # Keep historical value when possible and avoid NOT NULL insert crashes.
                s.execute(
                    text(
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
                if not is_nullable(s, "mermas", "costo_unitario"):
                    s.execute(text("ALTER TABLE mermas MODIFY COLUMN costo_unitario DOUBLE NULL"))

            if has_column(s, "mermas", "id_usuario_registro") and has_column(s, "mermas", "usuario_id"):
                s.execute(
                    text(
                        """
                        UPDATE mermas
                        SET id_usuario_registro = COALESCE(id_usuario_registro, usuario_id)
                        WHERE usuario_id IS NOT NULL
                        """
                    )
                )
                if not is_nullable(s, "mermas", "id_usuario_registro"):
                    s.execute(text("ALTER TABLE mermas MODIFY COLUMN id_usuario_registro INT NULL"))

            if has_column(s, "mermas", "id_usuario_autorizacion") and not is_nullable(s, "mermas", "id_usuario_autorizacion"):
                s.execute(text("ALTER TABLE mermas MODIFY COLUMN id_usuario_autorizacion INT NULL"))

            if has_column(s, "mermas", "autorizada") and not is_nullable(s, "mermas", "autorizada"):
                s.execute(text("ALTER TABLE mermas MODIFY COLUMN autorizada TINYINT(1) NULL"))

            if has_column(s, "mermas", "fecha") and has_column(s, "mermas", "fecha_registro"):
                s.execute(
                    text(
                        """
                        UPDATE mermas
                        SET fecha = COALESCE(fecha, fecha_registro)
                        WHERE fecha_registro IS NOT NULL
                        """
                    )
                )
                if not is_nullable(s, "mermas", "fecha"):
                    s.execute(text("ALTER TABLE mermas MODIFY COLUMN fecha DATETIME NULL"))

        # 7) Add FK constraints when missing
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

        if has_column(s, "productos", "dias_duracion") and not has_check_constraint(
            s, "productos", "check_dias_duracion_producto_minimo"
        ):
            s.execute(
                text(
                    """
                    ALTER TABLE productos
                    ADD CONSTRAINT check_dias_duracion_producto_minimo
                    CHECK (dias_duracion >= 2)
                    """
                )
            )

        # 8) Recreate legacy stored procedures aligned with current schema
        s.execute(text("DROP PROCEDURE IF EXISTS sp_crearCliente"))
        s.execute(
            text(
                """
                CREATE PROCEDURE sp_crearCliente(
                    IN p_nombre VARCHAR(100),
                    IN p_ap_p VARCHAR(50),
                    IN p_ap_m VARCHAR(50),
                    IN p_telefono VARCHAR(10),
                    IN p_correo VARCHAR(100),
                    IN p_direccion VARCHAR(200),
                    IN p_username VARCHAR(100),
                    IN p_password TEXT
                )
                BEGIN
                    DECLARE v_id_persona INT;
                    DECLARE v_id_usuario INT;
                    DECLARE v_id_rol_cliente INT;

                    START TRANSACTION;

                    SELECT id_rol INTO v_id_rol_cliente
                    FROM roles
                    WHERE nombre = 'Cliente'
                    LIMIT 1;

                    IF v_id_rol_cliente IS NULL THEN
                        SIGNAL SQLSTATE '45000'
                            SET MESSAGE_TEXT = 'No existe el rol Cliente.';
                    END IF;

                    INSERT INTO personas (
                        nombre, apellido_p, apellido_m,
                        telefono, correo, direccion, fecha_creacion
                    ) VALUES (
                        p_nombre, p_ap_p, NULLIF(p_ap_m, ''),
                        p_telefono, p_correo, NULLIF(p_direccion, ''), NOW()
                    );

                    SET v_id_persona = LAST_INSERT_ID();

                    INSERT INTO usuarios (
                        username, contrasena, estado,
                        fs_uniquifier, fecha_creacion, id_rol
                    ) VALUES (
                        p_username, p_password, 1,
                        UUID(), NOW(), v_id_rol_cliente
                    );

                    SET v_id_usuario = LAST_INSERT_ID();

                    INSERT INTO clientes (id_usuario, id_persona)
                    VALUES (v_id_usuario, v_id_persona);

                    COMMIT;
                END
                """
            )
        )

        s.execute(text("DROP PROCEDURE IF EXISTS sp_actualizarMiCuenta"))
        s.execute(
            text(
                """
                CREATE PROCEDURE sp_actualizarMiCuenta(
                    IN p_id_usuario INT,
                    IN p_nombre VARCHAR(100),
                    IN p_ap_p VARCHAR(50),
                    IN p_ap_m VARCHAR(50),
                    IN p_telefono VARCHAR(10),
                    IN p_correo VARCHAR(100),
                    IN p_direccion VARCHAR(200),
                    IN p_username VARCHAR(100),
                    IN p_password TEXT
                )
                BEGIN
                    DECLARE v_id_persona INT;

                    START TRANSACTION;

                    SELECT COALESCE(e.id_persona, c.id_persona) INTO v_id_persona
                    FROM usuarios u
                    LEFT JOIN empleados e ON e.id_usuario = u.id_usuario
                    LEFT JOIN clientes c ON c.id_usuario = u.id_usuario
                    WHERE u.id_usuario = p_id_usuario
                    LIMIT 1;

                    IF v_id_persona IS NULL THEN
                        SIGNAL SQLSTATE '45000'
                            SET MESSAGE_TEXT = 'No se encontro persona vinculada al usuario.';
                    END IF;

                    UPDATE personas
                    SET nombre = p_nombre,
                        apellido_p = p_ap_p,
                        apellido_m = NULLIF(p_ap_m, ''),
                        telefono = p_telefono,
                        correo = p_correo,
                        direccion = NULLIF(p_direccion, '')
                    WHERE id_persona = v_id_persona;

                    UPDATE usuarios
                    SET username = p_username,
                        contrasena = CASE
                            WHEN p_password IS NULL OR p_password = '' THEN contrasena
                            ELSE p_password
                        END
                    WHERE id_usuario = p_id_usuario;

                    COMMIT;
                END
                """
            )
        )

        s.commit()
        print("DB sync completed successfully.")


if __name__ == "__main__":
    run()
