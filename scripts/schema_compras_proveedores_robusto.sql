-- Esquema robusto para Compras/DetalleCompra en MariaDB (transaccional e idempotente)
-- Incluye soporte para pago contado/credito, tarjeta y recepcion por linea.

START TRANSACTION;

-- 1) Tabla compras (si no existe)
CREATE TABLE IF NOT EXISTS compras (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME NOT NULL,
    total DOUBLE NOT NULL DEFAULT 0,
    fecha_entrega DATETIME NULL,
    metodo_pago VARCHAR(50) NULL,
    tipo_pago VARCHAR(20) NOT NULL DEFAULT 'Contado',
    tarjeta_titular VARCHAR(120) NULL,
    tarjeta_ultimos4 VARCHAR(4) NULL,
    tarjeta_vencimiento VARCHAR(5) NULL,
    estado VARCHAR(50) NOT NULL DEFAULT 'Solicitada',
    desde_produccion TINYINT(1) NOT NULL DEFAULT 0,
    id_proveedor INT NULL,
    id_usuario INT NOT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_compra_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor),
    CONSTRAINT fk_compra_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    CONSTRAINT check_estado_compra CHECK (estado IN ('Solicitada', 'En Camino', 'Completada', 'Cancelada')),
    CONSTRAINT check_metodo_pago_compra CHECK (metodo_pago IN ('Efectivo', 'Tarjeta', 'Transferencia') OR metodo_pago IS NULL),
    CONSTRAINT check_tipo_pago_compra CHECK (tipo_pago IN ('Contado', 'Credito')),
    CONSTRAINT check_total_compra_no_negativo CHECK (total >= 0)
);

-- 2) Tabla detalle_compra (si no existe)
CREATE TABLE IF NOT EXISTS detalle_compra (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_compra INT NOT NULL,
    id_materia INT NOT NULL,
    cantidad DOUBLE NOT NULL,
    precio_u DOUBLE NOT NULL,
    subtotal DOUBLE NOT NULL,
    recibido TINYINT(1) NOT NULL DEFAULT 0,
    CONSTRAINT fk_detalle_compra_compra FOREIGN KEY (id_compra) REFERENCES compras(id_compra) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_compra_materia FOREIGN KEY (id_materia) REFERENCES materias_primas(id_materia),
    CONSTRAINT check_cantidad_positiva CHECK (cantidad > 0),
    CONSTRAINT check_precio_u_no_negativo CHECK (precio_u >= 0),
    CONSTRAINT check_subtotal_no_negativo CHECK (subtotal >= 0)
);

-- 3) Alter table defensivo para entornos donde ya existen tablas antiguas.
SET @col_tipo_pago := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'compras' AND COLUMN_NAME = 'tipo_pago'
);
SET @sql_tipo_pago := IF(
  @col_tipo_pago = 0,
  "ALTER TABLE compras ADD COLUMN tipo_pago VARCHAR(20) NOT NULL DEFAULT 'Contado' AFTER metodo_pago",
  'SELECT 1'
);
PREPARE stmt_tipo_pago FROM @sql_tipo_pago;
EXECUTE stmt_tipo_pago;
DEALLOCATE PREPARE stmt_tipo_pago;

SET @col_tarjeta_titular := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'compras' AND COLUMN_NAME = 'tarjeta_titular'
);
SET @sql_tarjeta_titular := IF(
  @col_tarjeta_titular = 0,
  'ALTER TABLE compras ADD COLUMN tarjeta_titular VARCHAR(120) NULL AFTER tipo_pago',
  'SELECT 1'
);
PREPARE stmt_tarjeta_titular FROM @sql_tarjeta_titular;
EXECUTE stmt_tarjeta_titular;
DEALLOCATE PREPARE stmt_tarjeta_titular;

SET @col_tarjeta_ultimos4 := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'compras' AND COLUMN_NAME = 'tarjeta_ultimos4'
);
SET @sql_tarjeta_ultimos4 := IF(
  @col_tarjeta_ultimos4 = 0,
  'ALTER TABLE compras ADD COLUMN tarjeta_ultimos4 VARCHAR(4) NULL AFTER tarjeta_titular',
  'SELECT 1'
);
PREPARE stmt_tarjeta_ultimos4 FROM @sql_tarjeta_ultimos4;
EXECUTE stmt_tarjeta_ultimos4;
DEALLOCATE PREPARE stmt_tarjeta_ultimos4;

SET @col_tarjeta_vencimiento := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'compras' AND COLUMN_NAME = 'tarjeta_vencimiento'
);
SET @sql_tarjeta_vencimiento := IF(
  @col_tarjeta_vencimiento = 0,
  'ALTER TABLE compras ADD COLUMN tarjeta_vencimiento VARCHAR(5) NULL AFTER tarjeta_ultimos4',
  'SELECT 1'
);
PREPARE stmt_tarjeta_vencimiento FROM @sql_tarjeta_vencimiento;
EXECUTE stmt_tarjeta_vencimiento;
DEALLOCATE PREPARE stmt_tarjeta_vencimiento;

SET @col_recibido := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'detalle_compra' AND COLUMN_NAME = 'recibido'
);
SET @sql_recibido := IF(
  @col_recibido = 0,
  'ALTER TABLE detalle_compra ADD COLUMN recibido TINYINT(1) NOT NULL DEFAULT 0 AFTER subtotal',
  'SELECT 1'
);
PREPARE stmt_recibido FROM @sql_recibido;
EXECUTE stmt_recibido;
DEALLOCATE PREPARE stmt_recibido;

-- 4) Indices recomendados para filtros por proveedor/estado/fechas.
CREATE INDEX IF NOT EXISTS idx_compras_estado ON compras (estado);
CREATE INDEX IF NOT EXISTS idx_compras_proveedor ON compras (id_proveedor);
CREATE INDEX IF NOT EXISTS idx_compras_fecha ON compras (fecha);
CREATE INDEX IF NOT EXISTS idx_detalle_compra_compra ON detalle_compra (id_compra);
CREATE INDEX IF NOT EXISTS idx_detalle_compra_materia ON detalle_compra (id_materia);

COMMIT;

-- ==========================================================
-- QUERIES TRANSACCIONALES DE OPERACION (RECEPCION DE COMPRA)
-- ==========================================================
-- Ejemplo: recibir una linea y subir stock en una sola transaccion.
-- Si cualquier paso falla, aplicar ROLLBACK.

-- START TRANSACTION;
-- UPDATE detalle_compra
--    SET recibido = 1,
--        cantidad = :cantidad_recibida,
--        precio_u = :precio_unitario,
--        subtotal = (:cantidad_recibida * :precio_unitario)
--  WHERE id_detalle = :id_detalle
--    AND id_compra = :id_compra
--    AND recibido = 0;
--
-- UPDATE materias_primas mp
-- JOIN detalle_compra dc ON dc.id_materia = mp.id_materia
--    SET mp.stock_actual = mp.stock_actual + dc.cantidad,
--        mp.precio = dc.precio_u
--  WHERE dc.id_detalle = :id_detalle
--    AND dc.id_compra = :id_compra;
--
-- UPDATE compras
--    SET total = (
--        SELECT COALESCE(SUM(subtotal), 0)
--          FROM detalle_compra
--         WHERE id_compra = :id_compra
--    ),
--        estado = CASE
--            WHEN NOT EXISTS (
--                SELECT 1
--                  FROM detalle_compra
--                 WHERE id_compra = :id_compra
--                   AND recibido = 0
--            ) THEN 'Completada'
--            ELSE 'En Camino'
--        END,
--        fecha_entrega = COALESCE(fecha_entrega, NOW())
--  WHERE id_compra = :id_compra;
--
-- COMMIT;
-- -- En caso de error: ROLLBACK;
