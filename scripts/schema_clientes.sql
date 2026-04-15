-- =============================================================
-- ESQUEMA MODULO CLIENTES - FondaGourmet
-- MariaDB / MySQL
-- =============================================================

-- 1) RFC opcional en personas
ALTER TABLE personas
    ADD COLUMN IF NOT EXISTS rfc_tax_id VARCHAR(20) NULL AFTER direccion;

-- 2) Estado logico de cliente
ALTER TABLE clientes
    ADD COLUMN IF NOT EXISTS estado_activo TINYINT(1) NOT NULL DEFAULT 1 AFTER id_persona;

-- 3) Indices para busqueda en modulo clientes
CREATE INDEX IF NOT EXISTS idx_personas_nombre ON personas(nombre, apellido_p, apellido_m);
CREATE INDEX IF NOT EXISTS idx_personas_contacto ON personas(telefono, correo);
CREATE INDEX IF NOT EXISTS idx_personas_rfc ON personas(rfc_tax_id);
CREATE INDEX IF NOT EXISTS idx_clientes_estado ON clientes(estado_activo);

-- 4) Integracion con pedidos (cliente_id)
-- Si la FK ya existe, este bloque no hara cambios.
SET @fk_exists := (
    SELECT COUNT(*)
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'pedidos'
      AND CONSTRAINT_NAME = 'fk_pedidos_clientes'
);

SET @sql_fk := IF(
    @fk_exists = 0,
    'ALTER TABLE pedidos ADD CONSTRAINT fk_pedidos_clientes FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)',
    'SELECT ''FK fk_pedidos_clientes ya existe'''
);

PREPARE stmt FROM @sql_fk;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
