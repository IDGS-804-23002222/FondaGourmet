-- Modulo de Mermas y Ajustes para MariaDB
-- Doble ajuste: materia prima e inventario terminado.
-- Incluye ejemplos transaccionales de descuento + historial.

START TRANSACTION;

CREATE TABLE IF NOT EXISTS mermas (
    id_merma INT AUTO_INCREMENT PRIMARY KEY,
    tipo_origen VARCHAR(30) NOT NULL,
    id_materia INT NULL,
    id_inventario INT NULL,
    id_producto INT NULL,
    cantidad DOUBLE NOT NULL,
    costo_unitario DOUBLE NOT NULL,
    costo_perdida DOUBLE NOT NULL,
    motivo VARCHAR(50) NOT NULL,
    observaciones TEXT NULL,
    autorizada TINYINT(1) NOT NULL DEFAULT 0,
    id_usuario_registro INT NOT NULL,
    id_usuario_autorizacion INT NULL,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_merma_materia FOREIGN KEY (id_materia) REFERENCES materias_primas(id_materia),
    CONSTRAINT fk_merma_inventario FOREIGN KEY (id_inventario) REFERENCES inventario_terminado(id_inventario),
    CONSTRAINT fk_merma_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    CONSTRAINT fk_merma_usuario_registro FOREIGN KEY (id_usuario_registro) REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_merma_usuario_autorizacion FOREIGN KEY (id_usuario_autorizacion) REFERENCES usuarios(id_usuario),
    CONSTRAINT check_merma_tipo_origen CHECK (tipo_origen IN ('MateriaPrima', 'InventarioTerminado')),
    CONSTRAINT check_merma_cantidad CHECK (cantidad > 0),
    CONSTRAINT check_merma_costo_unitario CHECK (costo_unitario >= 0),
    CONSTRAINT check_merma_costo_perdida CHECK (costo_perdida >= 0),
    CONSTRAINT check_merma_motivo CHECK (motivo IN ('Caducado', 'Danado', 'Error de Produccion', 'Robo'))
);

CREATE INDEX IF NOT EXISTS idx_mermas_fecha ON mermas(fecha);
CREATE INDEX IF NOT EXISTS idx_mermas_motivo ON mermas(motivo);
CREATE INDEX IF NOT EXISTS idx_mermas_tipo_origen ON mermas(tipo_origen);
CREATE INDEX IF NOT EXISTS idx_mermas_usuario ON mermas(id_usuario_registro);

COMMIT;

-- =============================================
-- EJEMPLO TRANSACCIONAL MERMA MATERIA PRIMA
-- =============================================
-- START TRANSACTION;
-- UPDATE materias_primas
--    SET stock_actual = stock_actual - :cantidad
--  WHERE id_materia = :id_materia
--    AND stock_actual >= :cantidad;
--
-- INSERT INTO mermas (
--   tipo_origen, id_materia, cantidad, costo_unitario, costo_perdida,
--   motivo, observaciones, autorizada, id_usuario_registro, id_usuario_autorizacion, fecha
-- ) VALUES (
--   'MateriaPrima', :id_materia, :cantidad, :costo_unitario, (:cantidad * :costo_unitario),
--   :motivo, :observaciones, :autorizada, :id_usuario_registro, :id_usuario_autorizacion, NOW()
-- );
-- COMMIT;
-- -- En error: ROLLBACK;

-- =============================================
-- EJEMPLO TRANSACCIONAL MERMA INVENTARIO TERMINADO
-- =============================================
-- START TRANSACTION;
-- UPDATE inventario_terminado
--    SET cantidad_disponible = cantidad_disponible - :cantidad,
--        fecha_actualizacion = NOW()
--  WHERE id_inventario = :id_inventario
--    AND cantidad_disponible >= :cantidad;
--
-- INSERT INTO mermas (
--   tipo_origen, id_inventario, id_producto, cantidad, costo_unitario, costo_perdida,
--   motivo, observaciones, autorizada, id_usuario_registro, id_usuario_autorizacion, fecha
-- ) VALUES (
--   'InventarioTerminado', :id_inventario, :id_producto, :cantidad, :costo_unitario, (:cantidad * :costo_unitario),
--   :motivo, :observaciones, :autorizada, :id_usuario_registro, :id_usuario_autorizacion, NOW()
-- );
-- COMMIT;
-- -- En error: ROLLBACK;
