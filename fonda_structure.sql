-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: fonda
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Temporary view structure for view `v_categorias`
--

DROP TABLE IF EXISTS `v_categorias`;
/*!50001 DROP VIEW IF EXISTS `v_categorias`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_categorias` AS SELECT 
 1 AS `id_categoria`,
 1 AS `nombre`,
 1 AS `descripcion`,
 1 AS `estado`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_clientes`
--

DROP TABLE IF EXISTS `v_clientes`;
/*!50001 DROP VIEW IF EXISTS `v_clientes`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_clientes` AS SELECT 
 1 AS `id_cliente`,
 1 AS `id_usuario`,
 1 AS `username`,
 1 AS `estado`,
 1 AS `nombre`,
 1 AS `apellido_p`,
 1 AS `apellido_m`,
 1 AS `telefono`,
 1 AS `correo`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_empleados`
--

DROP TABLE IF EXISTS `v_empleados`;
/*!50001 DROP VIEW IF EXISTS `v_empleados`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_empleados` AS SELECT 
 1 AS `id_empleado`,
 1 AS `id_usuario`,
 1 AS `username`,
 1 AS `estado`,
 1 AS `rol`,
 1 AS `nombre`,
 1 AS `apellido_p`,
 1 AS `apellido_m`,
 1 AS `telefono`,
 1 AS `correo`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_materias_primas`
--

DROP TABLE IF EXISTS `v_materias_primas`;
/*!50001 DROP VIEW IF EXISTS `v_materias_primas`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_materias_primas` AS SELECT 
 1 AS `id_materia`,
 1 AS `nombre`,
 1 AS `unidad_medida`,
 1 AS `stock_actual`,
 1 AS `stock_minimo`,
 1 AS `porcentaje_merma`,
 1 AS `factor_conversion`,
 1 AS `estado`,
 1 AS `categoria`,
 1 AS `id_proveedor`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_productos`
--

DROP TABLE IF EXISTS `v_productos`;
/*!50001 DROP VIEW IF EXISTS `v_productos`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_productos` AS SELECT 
 1 AS `id_producto`,
 1 AS `nombre`,
 1 AS `descripcion`,
 1 AS `precio`,
 1 AS `stock_actual`,
 1 AS `stock_minimo`,
 1 AS `imagen`,
 1 AS `estado`,
 1 AS `categoria`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_proveedores`
--

DROP TABLE IF EXISTS `v_proveedores`;
/*!50001 DROP VIEW IF EXISTS `v_proveedores`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_proveedores` AS SELECT 
 1 AS `id_proveedor`,
 1 AS `nombre`,
 1 AS `apellido_p`,
 1 AS `apellido_m`,
 1 AS `telefono`,
 1 AS `correo`,
 1 AS `estado`*/;
SET character_set_client = @saved_cs_client;

--
-- Dumping routines for database 'fonda'
--
/*!50003 DROP PROCEDURE IF EXISTS `sp_activarCategoria` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_activarCategoria`(IN p_id INT)
BEGIN
    UPDATE categorias SET estado = TRUE WHERE id_categoria = p_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_activarMateriaPrima` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_activarMateriaPrima`(IN p_id INT)
BEGIN
    UPDATE materias_primas SET estado = TRUE WHERE id_materia = p_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_activarProveedor` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_activarProveedor`(IN p_id INT)
BEGIN
    UPDATE proveedores SET estado = TRUE WHERE id_proveedor = p_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_activarUsuario` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_activarUsuario`(IN p_id INT)
BEGIN
    UPDATE usuarios SET estado = TRUE WHERE id_usuario = p_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_actualizarCategoria` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_actualizarCategoria`(
    IN p_id INT,
    IN p_nombre VARCHAR(100),
    IN p_descripcion TEXT
)
BEGIN
    UPDATE categorias
    SET nombre = p_nombre,
        descripcion = p_descripcion
    WHERE id_categoria = p_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_actualizarMateriaPrima` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_actualizarMateriaPrima`(
    IN p_id INT,
    IN p_nombre VARCHAR(100),
    IN p_unidad VARCHAR(20),
    IN p_stock_min DECIMAL(10,2),
    IN p_merma DECIMAL(5,2),
    IN p_factor DECIMAL(10,4),
    IN p_id_categoria INT,
    IN p_id_proveedor INT
)
BEGIN
    UPDATE materias_primas
    SET 
        nombre = IFNULL(p_nombre, nombre),
        unidad_medida = IFNULL(p_unidad, unidad_medida),
        stock_minimo = IFNULL(p_stock_min, stock_minimo),
        porcentaje_merma = IFNULL(p_merma, porcentaje_merma),
        factor_conversion = IFNULL(p_factor, factor_conversion),
        id_categoria = IFNULL(p_id_categoria, id_categoria),
        id_proveedor = IFNULL(p_id_proveedor, id_proveedor)
    WHERE id_materia = p_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_actualizarMiCuenta` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_actualizarMiCuenta`(
    IN p_id_usuario INT,
    IN p_nombre VARCHAR(100),
    IN p_ap_p VARCHAR(100),
    IN p_ap_m VARCHAR(100),
    IN p_telefono VARCHAR(15),
    IN p_correo VARCHAR(120),
    IN p_direccion VARCHAR(200),
    IN p_username VARCHAR(80),
    IN p_password VARCHAR(255),
    OUT p_resultado INT,
    OUT p_mensaje VARCHAR(255)
)
BEGIN
    DECLARE v_usuario_existe INT;
    DECLARE v_email_existe INT;
    DECLARE v_username_existe INT;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_resultado = 0;
        SET p_mensaje = 'Error en la base de datos al actualizar el perfil.';
    END;
    
    START TRANSACTION;
    
    -- Verificar si el usuario existe
    SELECT COUNT(*) INTO v_usuario_existe 
    FROM usuarios 
    WHERE id_usuario = p_id_usuario;
    
    IF v_usuario_existe = 0 THEN
        SET p_resultado = 0;
        SET p_mensaje = 'Usuario no encontrado.';
        ROLLBACK;
    ELSE
        -- Verificar si el email ya existe para otro usuario
        SELECT COUNT(*) INTO v_email_existe 
        FROM usuarios 
        WHERE correo = p_correo AND id_usuario != p_id_usuario;
        
        IF v_email_existe > 0 THEN
            SET p_resultado = 0;
            SET p_mensaje = 'El correo electrónico ya está registrado por otro usuario.';
            ROLLBACK;
        ELSE
            -- Verificar si el username ya existe para otro usuario
            SELECT COUNT(*) INTO v_username_existe 
            FROM usuarios 
            WHERE username = p_username AND id_usuario != p_id_usuario;
            
            IF v_username_existe > 0 THEN
                SET p_resultado = 0;
                SET p_mensaje = 'El nombre de usuario ya está en uso.';
                ROLLBACK;
            ELSE
                -- Actualizar los datos del usuario
                UPDATE usuarios 
                SET 
                    nombre = p_nombre,
                    apellido_paterno = p_ap_p,
                    apellido_materno = p_ap_m,
                    telefono = p_telefono,
                    correo = p_correo,
                    direccion = p_direccion,
                    username = p_username,
                    updated_at = NOW()
                WHERE id_usuario = p_id_usuario;
                
                -- Actualizar la contraseña solo si se proporcionó
                IF p_password IS NOT NULL AND p_password != '' THEN
                    UPDATE usuarios 
                    SET password = p_password
                    WHERE id_usuario = p_id_usuario;
                END IF;
                
                SET p_resultado = 1;
                SET p_mensaje = 'Perfil actualizado correctamente.';
                COMMIT;
            END IF;
        END IF;
    END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_actualizarProveedor` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_actualizarProveedor`(
    IN p_id_proveedor INT,
    IN p_nombre VARCHAR(100),
    IN p_ap_p VARCHAR(100),
    IN p_ap_m VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_correo VARCHAR(100),
    IN p_direccion TEXT
)
BEGIN
    DECLARE v_id_persona INT;
    
    SELECT id_persona INTO v_id_persona
    FROM proveedores
    WHERE id_proveedor = p_id_proveedor;
    
    -- =========================
    -- ACTUALIZAR PERSONA
    -- =========================
    UPDATE personas
    SET 
       nombre = IFNULL(NULLIF(p_nombre,''), nombre),
        apellido_p = IFNULL(NULLIF(p_ap_p,''), apellido_p),
        apellido_m = IFNULL(NULLIF(p_ap_m,''), apellido_m),
        telefono = IFNULL(NULLIF(p_telefono,''), telefono),
        correo = IFNULL(NULLIF(p_correo,''), correo),
        direccion = IFNULL(NULLIF(p_direccion,''), direccion)
    WHERE id_persona = v_id_persona;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_actualizarUsuario` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_actualizarUsuario`(
    IN p_id_usuario INT,
    IN p_nombre VARCHAR(100),
    IN p_ap_p VARCHAR(100),
    IN p_ap_m VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_correo VARCHAR(100),
    IN p_direccion TEXT,
    IN p_username VARCHAR(50),
    IN p_password TEXT,
    IN p_id_rol INT
)
BEGIN
    DECLARE v_id_persona INT;

    -- Obtener id_persona (cliente o empleado)
    SELECT COALESCE(c.id_persona, e.id_persona)
    INTO v_id_persona
    FROM usuarios u
    LEFT JOIN clientes c ON c.id_usuario = u.id_usuario
    LEFT JOIN empleados e ON e.id_usuario = u.id_usuario
    WHERE u.id_usuario = p_id_usuario;

    -- =========================
    -- ACTUALIZAR USUARIO
    -- =========================
    UPDATE usuarios 
    SET 
        username = CASE 
            WHEN p_username IS NULL OR p_username = '' OR p_username = username THEN username
            ELSE p_username
        END,

        id_rol = p_id_rol,

        contrasena = CASE
            WHEN p_password IS NULL OR p_password = '' THEN contrasena
            ELSE p_password
        END
    WHERE id_usuario = p_id_usuario;

    -- =========================
    -- ACTUALIZAR PERSONA
    -- =========================
    UPDATE personas
    SET 
        nombre = CASE 
            WHEN p_nombre IS NULL OR p_nombre = '' THEN nombre
            ELSE p_nombre
        END,

        apellido_p = CASE 
            WHEN p_ap_p IS NULL OR p_ap_p = '' THEN apellido_p
            ELSE p_ap_p
        END,

        apellido_m = CASE 
            WHEN p_ap_m IS NULL OR p_ap_m = '' THEN apellido_m
            ELSE p_ap_m
        END,

        telefono = CASE 
            WHEN p_telefono IS NULL OR p_telefono = '' OR p_telefono = telefono THEN telefono
            ELSE p_telefono
        END,

        correo = CASE 
            WHEN p_correo IS NULL OR p_correo = '' OR p_correo = correo THEN correo
            ELSE p_correo
        END,

        direccion = CASE 
            WHEN p_direccion IS NULL OR p_direccion = '' THEN direccion
            ELSE p_direccion
        END

    WHERE id_persona = v_id_persona;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_crearCategoria` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_crearCategoria`(
    IN p_nombre VARCHAR(100),
    IN p_descripcion TEXT
)
BEGIN
    INSERT INTO categorias(nombre, descripcion, estado, fecha_creacion)
    VALUES(p_nombre, p_descripcion, TRUE, NOW());
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_crearCliente` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_crearCliente`(
    IN p_nombre VARCHAR(100),
    IN p_apellido_p VARCHAR(50),
    IN p_apellido_m VARCHAR(50),
    IN p_telefono VARCHAR(10),
    IN p_correo VARCHAR(100),
    IN p_direccion VARCHAR(200),
    IN p_username VARCHAR(100),
    IN p_password VARCHAR(255)
)
BEGIN
    DECLARE v_id_persona INT;
    DECLARE v_id_usuario INT;
    DECLARE v_id_rol INT;

    -- Validar duplicados
    IF EXISTS (
        SELECT 1 FROM personas 
        WHERE correo = p_correo OR telefono = p_telefono
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Correo o telefono ya existen';
    END IF;

    IF EXISTS (
        SELECT 1 FROM usuarios 
        WHERE username = p_username
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El username ya existe';
    END IF;

    -- Obtener rol cliente
    SELECT id_rol INTO v_id_rol
    FROM roles
    WHERE nombre = 'Cliente'
    LIMIT 1;

    -- Insertar persona
    INSERT INTO personas(
        nombre, apellido_p, apellido_m,
        telefono, correo, direccion,
        estado, fecha_creacion
    )
    VALUES (
        p_nombre, p_apellido_p, p_apellido_m,
        p_telefono, p_correo, p_direccion,
        TRUE, NOW()
    );

    SET v_id_persona = LAST_INSERT_ID();

    -- Insertar usuario
    INSERT INTO usuarios(
        username, contrasena, estado,
        fs_uniquifier, fecha_creacion, id_rol
    )
    VALUES (
        p_username, p_password, TRUE,
        UUID(), NOW(), v_id_rol
    );

    SET v_id_usuario = LAST_INSERT_ID();

    -- Insertar cliente
    INSERT INTO clientes(id_usuario, id_persona)
    VALUES (v_id_usuario, v_id_persona);

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_crearEmpleado` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_crearEmpleado`(
    IN p_nombre VARCHAR(100),
    IN p_apellido_p VARCHAR(50),
    IN p_apellido_m VARCHAR(50),
    IN p_telefono VARCHAR(10),
    IN p_correo VARCHAR(100),
    IN p_direccion VARCHAR(200),
    IN p_username VARCHAR(100),
    IN p_password VARCHAR(255),
    IN p_rol VARCHAR(50) -- Administrador, Cajero, Cocinero, Dueño
)
BEGIN
    DECLARE v_id_persona INT;
    DECLARE v_id_usuario INT;
    DECLARE v_id_rol INT;

    -- Validar duplicados persona
    IF EXISTS (
        SELECT 1 FROM personas 
        WHERE correo = p_correo OR telefono = p_telefono
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Correo o telefono ya existen';
    END IF;

    -- Validar duplicados usuario
    IF EXISTS (
        SELECT 1 FROM usuarios 
        WHERE username = p_username
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El username ya existe';
    END IF;

    -- Obtener rol (NO cliente)
    SELECT id_rol INTO v_id_rol
    FROM roles
    WHERE nombre = p_rol
    LIMIT 1;

    IF v_id_rol IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Rol no valido';
    END IF;

    -- Insertar persona
    INSERT INTO personas(
        nombre, apellido_p, apellido_m,
        telefono, correo, direccion,
        estado, fecha_creacion
    )
    VALUES (
        p_nombre, p_apellido_p, p_apellido_m,
        p_telefono, p_correo, p_direccion,
        TRUE, NOW()
    );

    SET v_id_persona = LAST_INSERT_ID();

    -- Insertar usuario
    INSERT INTO usuarios(
        username, contrasena, estado,
        fs_uniquifier, fecha_creacion, id_rol
    )
    VALUES (
        p_username, p_password, TRUE,
        UUID(), NOW(), v_id_rol
    );

    SET v_id_usuario = LAST_INSERT_ID();

    -- Insertar empleado
    INSERT INTO empleados(id_usuario, id_persona)
    VALUES (v_id_usuario, v_id_persona);

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_crearIngrediente` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_crearIngrediente`(
    IN p_nombre VARCHAR(100),
    IN p_unidad VARCHAR(20),
    IN p_stock_min DECIMAL(10,2),
    IN p_merma DECIMAL(5,2),
    IN p_factor DECIMAL(10,4),
    IN p_id_categoria INT,
    IN p_id_proveedor INT
)
BEGIN
    INSERT INTO materias_primas(
        nombre, unidad_medida,
        stock_actual, stock_minimo,
        porcentaje_merma, factor_conversion,
        estado, fecha_creacion,
        id_categoria, id_proveedor
    )
    VALUES(
        p_nombre, p_unidad,
        0, p_stock_min,
        p_merma, p_factor,
        TRUE, NOW(),
        p_id_categoria, p_id_proveedor
    );
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_crearMateriaPrima` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_crearMateriaPrima`(
    IN p_nombre VARCHAR(100),
    IN p_unidad VARCHAR(20),
    IN p_stock_min DECIMAL(10,2),
    IN p_merma DECIMAL(5,2),
    IN p_factor DECIMAL(10,4),
    IN p_id_categoria INT,
    IN p_id_proveedor INT
)
BEGIN
    INSERT INTO materias_primas(
        nombre, unidad_medida,
        stock_actual, stock_minimo,
        porcentaje_merma, factor_conversion,
        estado, fecha_creacion,
        id_categoria, id_proveedor
    )
    VALUES(
        p_nombre, p_unidad,
        0, p_stock_min,
        p_merma, p_factor,
        TRUE, NOW(),
        p_id_categoria, p_id_proveedor
    );
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_crearProducto` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_crearProducto`(
    IN p_nombre VARCHAR(100),
    IN p_descripcion TEXT,
    IN p_precio DECIMAL(10,2),
    IN p_stock_min DECIMAL(10,2),
    IN p_imagen VARCHAR(255),
    IN p_id_categoria INT
)
BEGIN
    INSERT INTO productos(
        nombre, descripcion, precio,
        stock_actual, stock_minimo,
        imagen, estado, fecha_creacion, id_categoria
    )
    VALUES(
        p_nombre, p_descripcion, p_precio,
        0, p_stock_min,
        p_imagen, TRUE, NOW(), p_id_categoria
    );
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_crearProveedor` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_crearProveedor`(
    IN p_nombre VARCHAR(100),
    IN p_apellido_p VARCHAR(50),
    IN p_apellido_m VARCHAR(50),
    IN p_telefono VARCHAR(10),
    IN p_correo VARCHAR(100),
    IN p_direccion VARCHAR(200)
)
BEGIN
    DECLARE v_id_persona INT;

    -- Validar duplicados
    IF EXISTS (
        SELECT 1 FROM personas 
        WHERE correo = p_correo OR telefono = p_telefono
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Correo o telefono ya existen';
    END IF;
    -- Insertar persona
    INSERT INTO personas(
        nombre, apellido_p, apellido_m,
        telefono, correo, direccion,
        fecha_creacion
    )
    VALUES (
        p_nombre, p_apellido_p, p_apellido_m,
        p_telefono, p_correo, p_direccion,
        NOW()
    );

    SET v_id_persona = LAST_INSERT_ID();

    -- Insertar proveedor
    INSERT INTO proveedores(id_persona, estado)
    VALUES (v_id_persona,1);

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_desactivarUsuario` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_desactivarUsuario`(
    IN user_id INT
)
BEGIN
    UPDATE usuarios
    SET estado = FALSE
    WHERE id_usuario = user_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_eliminarCategoria` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_eliminarCategoria`(IN p_id INT)
BEGIN
    UPDATE categorias SET estado = FALSE WHERE id_categoria = p_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_eliminarMateriaPrima` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_eliminarMateriaPrima`(IN p_id INT)
BEGIN
    UPDATE materias_primas SET estado = FALSE WHERE id_materia = p_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_eliminarProveedor` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_eliminarProveedor`(IN p_id INT)
BEGIN
    UPDATE proveedores SET estado = FALSE WHERE id_proveedor = p_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_eliminarUsuario` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_eliminarUsuario`(IN p_id_usuario INT)
BEGIN
    UPDATE usuarios
    SET estado = 0
    WHERE id_usuario = p_id_usuario;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_filtrarCategorias` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_filtrarCategorias`(IN filtro VARCHAR(100))
BEGIN
    SELECT * FROM v_categorias
    WHERE nombre LIKE CONCAT('%', filtro, '%');
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_filtrarMaterias` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_filtrarMaterias`(IN filtro VARCHAR(100))
BEGIN
    SELECT * FROM v_materias_primas
    WHERE nombre LIKE CONCAT('%', filtro, '%')
       OR categoria LIKE CONCAT('%', filtro, '%');
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_filtrarProveedores` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_filtrarProveedores`(IN filtro VARCHAR(100))
BEGIN
    SELECT 
        pr.id_proveedor,
        p.nombre,
        p.apellido_p,
        p.apellido_m,
        p.telefono,
        p.correo,
        pr.estado
    FROM proveedores pr
    LEFT JOIN personas p ON p.id_persona = pr.id_persona
    WHERE p.nombre LIKE CONCAT('%', filtro, '%')
       OR p.apellido_p LIKE CONCAT('%', filtro, '%');
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_filtrarUsuarios` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_filtrarUsuarios`(IN filtro VARCHAR(100))
BEGIN
    SELECT 
        u.id_usuario,
        u.username,
        r.nombre AS rol,
        p.nombre,
        p.apellido_p,
        p.correo,
        u.estado
    FROM usuarios u
    JOIN roles r ON u.id_rol = r.id_rol
    LEFT JOIN clientes c ON c.id_usuario = u.id_usuario
    LEFT JOIN empleados e ON e.id_usuario = u.id_usuario
    LEFT JOIN personas p ON p.id_persona = COALESCE(c.id_persona, e.id_persona)
    WHERE u.username LIKE CONCAT('%', filtro, '%')
       OR p.nombre LIKE CONCAT('%', filtro, '%');
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_insertarUsuario` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_insertarUsuario`(
    IN user_username VARCHAR(100),
    IN user_password VARCHAR(255),
    IN user_id_rol INT
)
BEGIN
    DECLARE v_count INT;

    SELECT COUNT(*)
    INTO v_count
    FROM usuarios
    WHERE username = user_username;

    IF v_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El usuario ya existe';
    END IF;

    INSERT INTO usuarios(
        username,
        contrasena,
        estado,
        fs_uniquifier,
        fecha_creacion,
        id_rol
    )
    VALUES (
        user_username,
        user_password,
        TRUE,
        UUID(),
        NOW(),
        user_id_rol
    );

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_obtenerCategoria` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_obtenerCategoria`(IN p_id INT)
BEGIN
    SELECT * FROM v_categorias WHERE id_categoria = p_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_obtenerMateriaPrima` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_obtenerMateriaPrima`(IN p_id INT)
BEGIN
    SELECT * FROM v_materias_primas WHERE id_materia = p_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_obtenerUsuario` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_obtenerUsuario`(IN p_id INT)
BEGIN
    SELECT 
        u.id_usuario,
        u.username,
        r.nombre AS rol,
        p.nombre,
        p.apellido_p,
        p.apellido_m,
        p.telefono,
        p.correo,
        p.direccion
    FROM usuarios u
    JOIN roles r ON u.id_rol = r.id_rol
    LEFT JOIN clientes c ON c.id_usuario = u.id_usuario
    LEFT JOIN empleados e ON e.id_usuario = u.id_usuario
    LEFT JOIN personas p ON p.id_persona = COALESCE(c.id_persona, e.id_persona)
    WHERE u.id_usuario = p_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_reactivarEmpleado` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_reactivarEmpleado`(
    IN emp_idEmpleado INT
)
BEGIN
    UPDATE empleados
    SET estado = TRUE
    WHERE idEmpleado = emp_idEmpleado AND estado = FALSE;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_reactivarUsuario` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_reactivarUsuario`(IN p_id_usuario INT)
BEGIN
    UPDATE usuarios
    SET estado = 1
    WHERE id_usuario = p_id_usuario;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_verMiCuenta` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_verMiCuenta`(IN p_id INT)
BEGIN
    CALL sp_obtenerUsuario(p_id);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_verProveedores` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_verProveedores`()
BEGIN
    SELECT 
        pr.id_proveedor,            -- 0
        p.nombre,                -- 1
        p.apellido_p,            -- 2
        p.apellido_m,            -- 3
        p.telefono,				 -- 4
        p.correo,				 -- 5
        pr.estado				 -- 6
    FROM proveedores pr
    LEFT JOIN personas p ON p.id_persona = pr.id_persona;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_verUsuarios` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_verUsuarios`()
BEGIN
    SELECT 
        u.id_usuario,            -- 0
        u.username,              -- 1
        u.estado,                -- 2 ✅ (IMPORTANTE)
        p.nombre,                -- 3
        p.apellido_p,            -- 4
        p.apellido_m,            -- 5
        r.nombre AS rol_nombre 	 -- 6
    FROM usuarios u
    LEFT JOIN roles r ON u.id_rol = r.id_rol
    LEFT JOIN clientes c ON c.id_usuario = u.id_usuario
    LEFT JOIN empleados e ON e.id_usuario = u.id_usuario
    LEFT JOIN personas p ON p.id_persona = COALESCE(c.id_persona, e.id_persona);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Final view structure for view `v_categorias`
--

/*!50001 DROP VIEW IF EXISTS `v_categorias`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_categorias` AS select `categorias`.`id_categoria` AS `id_categoria`,`categorias`.`nombre` AS `nombre`,`categorias`.`descripcion` AS `descripcion`,`categorias`.`estado` AS `estado` from `categorias` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_clientes`
--

/*!50001 DROP VIEW IF EXISTS `v_clientes`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_clientes` AS select `c`.`id_cliente` AS `id_cliente`,`u`.`id_usuario` AS `id_usuario`,`u`.`username` AS `username`,`u`.`estado` AS `estado`,`p`.`nombre` AS `nombre`,`p`.`apellido_p` AS `apellido_p`,`p`.`apellido_m` AS `apellido_m`,`p`.`telefono` AS `telefono`,`p`.`correo` AS `correo` from ((`clientes` `c` join `usuarios` `u` on((`c`.`id_usuario` = `u`.`id_usuario`))) join `personas` `p` on((`c`.`id_persona` = `p`.`id_persona`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_empleados`
--

/*!50001 DROP VIEW IF EXISTS `v_empleados`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_empleados` AS select `e`.`id_empleado` AS `id_empleado`,`u`.`id_usuario` AS `id_usuario`,`u`.`username` AS `username`,`u`.`estado` AS `estado`,`r`.`nombre` AS `rol`,`p`.`nombre` AS `nombre`,`p`.`apellido_p` AS `apellido_p`,`p`.`apellido_m` AS `apellido_m`,`p`.`telefono` AS `telefono`,`p`.`correo` AS `correo` from (((`empleados` `e` join `usuarios` `u` on((`e`.`id_usuario` = `u`.`id_usuario`))) join `personas` `p` on((`e`.`id_persona` = `p`.`id_persona`))) join `roles` `r` on((`u`.`id_rol` = `r`.`id_rol`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_materias_primas`
--

/*!50001 DROP VIEW IF EXISTS `v_materias_primas`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_materias_primas` AS select `m`.`id_materia` AS `id_materia`,`m`.`nombre` AS `nombre`,`m`.`unidad_medida` AS `unidad_medida`,`m`.`stock_actual` AS `stock_actual`,`m`.`stock_minimo` AS `stock_minimo`,`m`.`porcentaje_merma` AS `porcentaje_merma`,`m`.`factor_conversion` AS `factor_conversion`,`m`.`estado` AS `estado`,`c`.`nombre` AS `categoria`,`p`.`id_proveedor` AS `id_proveedor` from ((`materias_primas` `m` join `categorias` `c` on((`m`.`id_categoria` = `c`.`id_categoria`))) join `proveedores` `p` on((`m`.`id_proveedor` = `p`.`id_proveedor`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_productos`
--

/*!50001 DROP VIEW IF EXISTS `v_productos`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_productos` AS select `p`.`id_producto` AS `id_producto`,`p`.`nombre` AS `nombre`,`p`.`descripcion` AS `descripcion`,`p`.`precio` AS `precio`,`p`.`stock_actual` AS `stock_actual`,`p`.`stock_minimo` AS `stock_minimo`,`p`.`imagen` AS `imagen`,`p`.`estado` AS `estado`,`c`.`nombre` AS `categoria` from (`productos` `p` join `categorias` `c` on((`p`.`id_categoria` = `c`.`id_categoria`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_proveedores`
--

/*!50001 DROP VIEW IF EXISTS `v_proveedores`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_proveedores` AS select `pr`.`id_proveedor` AS `id_proveedor`,`p`.`nombre` AS `nombre`,`p`.`apellido_p` AS `apellido_p`,`p`.`apellido_m` AS `apellido_m`,`p`.`telefono` AS `telefono`,`p`.`correo` AS `correo`,`pr`.`estado` AS `estado` from (`proveedores` `pr` join `personas` `p` on((`pr`.`id_persona` = `p`.`id_persona`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-02 18:34:01
