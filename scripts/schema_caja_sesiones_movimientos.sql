-- =============================================================
-- ESQUEMA CAJA (entregable solicitado)
-- MariaDB / MySQL
-- Tablas: caja_sesiones, caja_movimientos
-- =============================================================

CREATE TABLE IF NOT EXISTS caja_sesiones (
    id_sesion INT NOT NULL AUTO_INCREMENT,
    fecha_apertura DATETIME NOT NULL,
    fecha_cierre DATETIME NULL,
    monto_inicial DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    monto_final DECIMAL(12,2) NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Abierta',
    id_usuario_apertura INT NOT NULL,
    id_usuario_cierre INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id_sesion),
    INDEX idx_caja_sesiones_estado (estado),
    INDEX idx_caja_sesiones_apertura (fecha_apertura),
    CONSTRAINT chk_caja_sesiones_estado CHECK (estado IN ('Abierta', 'Cerrada')),
    CONSTRAINT chk_caja_sesiones_monto_inicial CHECK (monto_inicial >= 0),
    CONSTRAINT chk_caja_sesiones_monto_final CHECK (monto_final IS NULL OR monto_final >= 0),
    CONSTRAINT fk_caja_sesiones_usuario_apertura FOREIGN KEY (id_usuario_apertura) REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_caja_sesiones_usuario_cierre FOREIGN KEY (id_usuario_cierre) REFERENCES usuarios(id_usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS caja_movimientos (
    id_movimiento INT NOT NULL AUTO_INCREMENT,
    id_sesion INT NOT NULL,
    fecha DATETIME NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    monto DECIMAL(12,2) NOT NULL,
    descripcion VARCHAR(255) NULL,
    referencia_tipo VARCHAR(40) NULL,
    referencia_id INT NULL,
    id_usuario INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_movimiento),
    INDEX idx_caja_movimientos_sesion (id_sesion),
    INDEX idx_caja_movimientos_fecha (fecha),
    INDEX idx_caja_movimientos_tipo (tipo),
    CONSTRAINT chk_caja_movimientos_tipo CHECK (tipo IN ('Ingreso', 'Egreso')),
    CONSTRAINT chk_caja_movimientos_monto CHECK (monto >= 0),
    CONSTRAINT fk_caja_movimientos_sesion FOREIGN KEY (id_sesion) REFERENCES caja_sesiones(id_sesion) ON DELETE CASCADE,
    CONSTRAINT fk_caja_movimientos_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Vistas opcionales de compatibilidad para integraciones existentes
-- (si el codigo actual usa tablas 'caja' y 'movimientos_caja').

CREATE OR REPLACE VIEW caja AS
SELECT
    cs.id_sesion AS id_caja,
    cs.fecha_apertura AS fecha,
    cs.monto_inicial,
    cs.monto_final,
    cs.estado,
    cs.id_usuario_apertura AS id_usuario
FROM caja_sesiones cs;

CREATE OR REPLACE VIEW movimientos_caja AS
SELECT
    cm.id_movimiento,
    cm.fecha,
    cm.tipo,
    cm.monto,
    cm.descripcion,
    cm.id_sesion AS id_caja
FROM caja_movimientos cm;
