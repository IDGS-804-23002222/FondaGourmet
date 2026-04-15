-- Actualiza recetas para manejar rendimiento por porciones y crea inventario terminado.
-- Ejecutar en la base de datos de FondaGourmet (MariaDB/MySQL).

START TRANSACTION;

-- 1) Campo nuevo en recetas: rendimiento_porciones.
SET @col_exists := (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'recetas'
      AND COLUMN_NAME = 'rendimiento_porciones'
);

SET @sql_add_col := IF(
    @col_exists = 0,
    'ALTER TABLE recetas ADD COLUMN rendimiento_porciones INT NOT NULL DEFAULT 1 AFTER porciones',
    'SELECT 1'
);
PREPARE stmt_add_col FROM @sql_add_col;
EXECUTE stmt_add_col;
DEALLOCATE PREPARE stmt_add_col;

-- Backfill: usar porciones actuales cuando rendimiento_porciones sea nulo o invalido.
UPDATE recetas
SET rendimiento_porciones = CASE
    WHEN porciones IS NULL OR porciones <= 0 THEN 1
    ELSE porciones
END
WHERE rendimiento_porciones IS NULL OR rendimiento_porciones <= 0;

-- 2) Tabla inventario_terminado.
CREATE TABLE IF NOT EXISTS inventario_terminado (
    id_inventario INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    cantidad_disponible INT NOT NULL DEFAULT 0,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_inventario_terminado_producto UNIQUE (id_producto),
    CONSTRAINT fk_inventario_terminado_producto FOREIGN KEY (id_producto)
        REFERENCES productos(id_producto)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT check_inventario_terminado_no_negativo CHECK (cantidad_disponible >= 0)
);

-- Compatibilidad: si la tabla ya existia con la columna sin default, normalizarla.
ALTER TABLE inventario_terminado
MODIFY COLUMN fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- 3) Semilla inicial de inventario terminado.
-- Compatibilidad:
-- - Si existe productos.stock_actual (legacy), se usa para inicializar.
-- - Si no existe (esquema actual), inicializa en 0 para no romper despliegues.
SET @col_stock_actual := (
        SELECT COUNT(*)
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'productos'
            AND COLUMN_NAME = 'stock_actual'
);

SET @sql_seed_inventario := IF(
        @col_stock_actual > 0,
        'INSERT INTO inventario_terminado (id_producto, cantidad_disponible)
         SELECT p.id_producto, GREATEST(CAST(COALESCE(p.stock_actual, 0) AS SIGNED), 0)
         FROM productos p
         LEFT JOIN inventario_terminado it ON it.id_producto = p.id_producto
         WHERE it.id_producto IS NULL',
        'INSERT INTO inventario_terminado (id_producto, cantidad_disponible)
         SELECT p.id_producto, 0
         FROM productos p
         LEFT JOIN inventario_terminado it ON it.id_producto = p.id_producto
         WHERE it.id_producto IS NULL'
);
PREPARE stmt_seed_inventario FROM @sql_seed_inventario;
EXECUTE stmt_seed_inventario;
DEALLOCATE PREPARE stmt_seed_inventario;

COMMIT;
