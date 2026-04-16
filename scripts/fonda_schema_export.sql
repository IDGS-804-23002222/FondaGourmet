/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-12.2.2-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: fonda
-- ------------------------------------------------------
-- Server version	12.2.2-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `caja`
--

DROP TABLE IF EXISTS `caja`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `caja` (
  `id_caja` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL,
  `monto_inicial` float NOT NULL,
  `monto_final` float DEFAULT NULL,
  `estado` varchar(20) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  PRIMARY KEY (`id_caja`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `check_estado_caja` CHECK (`estado` in ('Abierta','Cerrada')),
  CONSTRAINT `check_monto_inicial_no_negativo` CHECK (`monto_inicial` >= 0),
  CONSTRAINT `check_monto_final_no_negativo` CHECK (`monto_final` >= 0)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `caja_movimientos`
--

DROP TABLE IF EXISTS `caja_movimientos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `caja_movimientos` (
  `id_movimiento` int(11) NOT NULL AUTO_INCREMENT,
  `id_sesion` int(11) NOT NULL,
  `fecha` datetime NOT NULL,
  `tipo` varchar(20) NOT NULL,
  `monto` decimal(12,2) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `referencia_tipo` varchar(40) DEFAULT NULL,
  `referencia_id` int(11) DEFAULT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id_movimiento`),
  KEY `idx_caja_movimientos_sesion` (`id_sesion`),
  KEY `idx_caja_movimientos_fecha` (`fecha`),
  KEY `idx_caja_movimientos_tipo` (`tipo`),
  KEY `fk_caja_movimientos_usuario` (`id_usuario`),
  CONSTRAINT `fk_caja_movimientos_sesion` FOREIGN KEY (`id_sesion`) REFERENCES `caja_sesiones` (`id_sesion`) ON DELETE CASCADE,
  CONSTRAINT `fk_caja_movimientos_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `chk_caja_movimientos_tipo` CHECK (`tipo` in ('Ingreso','Egreso')),
  CONSTRAINT `chk_caja_movimientos_monto` CHECK (`monto` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `caja_sesiones`
--

DROP TABLE IF EXISTS `caja_sesiones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `caja_sesiones` (
  `id_sesion` int(11) NOT NULL AUTO_INCREMENT,
  `fecha_apertura` datetime NOT NULL,
  `fecha_cierre` datetime DEFAULT NULL,
  `monto_inicial` decimal(12,2) NOT NULL DEFAULT 0.00,
  `monto_final` decimal(12,2) DEFAULT NULL,
  `estado` varchar(20) NOT NULL DEFAULT 'Abierta',
  `id_usuario_apertura` int(11) NOT NULL,
  `id_usuario_cierre` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_sesion`),
  KEY `idx_caja_sesiones_estado` (`estado`),
  KEY `idx_caja_sesiones_apertura` (`fecha_apertura`),
  KEY `fk_caja_sesiones_usuario_apertura` (`id_usuario_apertura`),
  KEY `fk_caja_sesiones_usuario_cierre` (`id_usuario_cierre`),
  CONSTRAINT `fk_caja_sesiones_usuario_apertura` FOREIGN KEY (`id_usuario_apertura`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `fk_caja_sesiones_usuario_cierre` FOREIGN KEY (`id_usuario_cierre`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `chk_caja_sesiones_estado` CHECK (`estado` in ('Abierta','Cerrada')),
  CONSTRAINT `chk_caja_sesiones_monto_inicial` CHECK (`monto_inicial` >= 0),
  CONSTRAINT `chk_caja_sesiones_monto_final` CHECK (`monto_final` is null or `monto_final` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `carritos`
--

DROP TABLE IF EXISTS `carritos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `carritos` (
  `id_carrito` int(11) NOT NULL AUTO_INCREMENT,
  `fecha_creacion` datetime NOT NULL,
  `estado` varchar(20) NOT NULL,
  `total` float NOT NULL,
  `metodo_pago` varchar(50) DEFAULT NULL,
  `id_cliente` int(11) NOT NULL,
  PRIMARY KEY (`id_carrito`),
  KEY `id_cliente` (`id_cliente`),
  CONSTRAINT `1` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `categorias`
--

DROP TABLE IF EXISTS `categorias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias` (
  `id_categoria` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `tipo_categoria` varchar(20) NOT NULL,
  `estado` tinyint(1) DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL,
  PRIMARY KEY (`id_categoria`),
  CONSTRAINT `check_tipo_categoria` CHECK (`tipo_categoria` in ('platillo','ingrediente'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `categorias_ingrediente`
--

DROP TABLE IF EXISTS `categorias_ingrediente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias_ingrediente` (
  `id_categoria_ingrediente` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `estado` tinyint(1) DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL,
  PRIMARY KEY (`id_categoria_ingrediente`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `categorias_platillo`
--

DROP TABLE IF EXISTS `categorias_platillo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias_platillo` (
  `id_categoria_platillo` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `estado` tinyint(1) DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL,
  PRIMARY KEY (`id_categoria_platillo`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `categorias_proveedor`
--

DROP TABLE IF EXISTS `categorias_proveedor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias_proveedor` (
  `id_categoria_proveedor` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `estado` tinyint(1) DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL,
  PRIMARY KEY (`id_categoria_proveedor`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `clientes`
--

DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `clientes` (
  `id_cliente` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `id_persona` int(11) NOT NULL,
  `estado_activo` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_cliente`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_persona` (`id_persona`),
  KEY `idx_clientes_estado` (`estado_activo`),
  CONSTRAINT `1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `2` FOREIGN KEY (`id_persona`) REFERENCES `personas` (`id_persona`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `compras`
--

DROP TABLE IF EXISTS `compras`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `compras` (
  `id_compra` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL,
  `total` float NOT NULL,
  `fecha_entrega` datetime DEFAULT NULL,
  `metodo_pago` varchar(50) DEFAULT NULL,
  `tipo_pago` varchar(20) NOT NULL DEFAULT 'Contado',
  `tarjeta_titular` varchar(120) DEFAULT NULL,
  `tarjeta_ultimos4` varchar(4) DEFAULT NULL,
  `tarjeta_vencimiento` varchar(5) DEFAULT NULL,
  `estado` varchar(50) NOT NULL,
  `desde_produccion` tinyint(1) NOT NULL,
  `id_proveedor` int(11) DEFAULT NULL,
  `id_usuario` int(11) NOT NULL,
  `fecha_creacion` datetime NOT NULL,
  PRIMARY KEY (`id_compra`),
  KEY `id_usuario` (`id_usuario`),
  KEY `idx_compras_estado` (`estado`),
  KEY `idx_compras_proveedor` (`id_proveedor`),
  KEY `idx_compras_fecha` (`fecha`),
  CONSTRAINT `1` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id_proveedor`),
  CONSTRAINT `2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `check_estado_compra` CHECK (`estado` in ('Solicitada','En Camino','Completada','Cancelada')),
  CONSTRAINT `check_metodo_pago_compra` CHECK (`metodo_pago` in ('Efectivo','Tarjeta','Transferencia')),
  CONSTRAINT `check_total_compra_no_negativo` CHECK (`total` >= 0)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `detalle_carrito`
--

DROP TABLE IF EXISTS `detalle_carrito`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_carrito` (
  `id_detalle` int(11) NOT NULL AUTO_INCREMENT,
  `cantidad` int(11) NOT NULL,
  `subtotal` float NOT NULL,
  `id_carrito` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `id_carrito` (`id_carrito`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `1` FOREIGN KEY (`id_carrito`) REFERENCES `carritos` (`id_carrito`),
  CONSTRAINT `2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`),
  CONSTRAINT `check_cantidad_carrito_positiva` CHECK (`cantidad` > 0),
  CONSTRAINT `check_subtotal_carrito_no_negativo` CHECK (`subtotal` >= 0)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `detalle_compra`
--

DROP TABLE IF EXISTS `detalle_compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_compra` (
  `id_detalle` int(11) NOT NULL AUTO_INCREMENT,
  `id_compra` int(11) NOT NULL,
  `id_materia` int(11) NOT NULL,
  `cantidad` float NOT NULL,
  `precio_u` float NOT NULL,
  `subtotal` float NOT NULL,
  `recibido` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id_detalle`),
  KEY `idx_detalle_compra_compra` (`id_compra`),
  KEY `idx_detalle_compra_materia` (`id_materia`),
  CONSTRAINT `1` FOREIGN KEY (`id_compra`) REFERENCES `compras` (`id_compra`),
  CONSTRAINT `2` FOREIGN KEY (`id_materia`) REFERENCES `materias_primas` (`id_materia`),
  CONSTRAINT `check_cantidad_positiva` CHECK (`cantidad` > 0),
  CONSTRAINT `check_precio_u_no_negativo` CHECK (`precio_u` >= 0),
  CONSTRAINT `check_subtotal_no_negativo` CHECK (`subtotal` >= 0)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `detalle_pedido`
--

DROP TABLE IF EXISTS `detalle_pedido`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_pedido` (
  `id_detalle` int(11) NOT NULL AUTO_INCREMENT,
  `cantidad` int(11) NOT NULL,
  `subtotal` float NOT NULL,
  `id_pedido` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `atendido` tinyint(1) NOT NULL DEFAULT 0,
  `en_produccion` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id_detalle`),
  KEY `id_pedido` (`id_pedido`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `1` FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id_pedido`),
  CONSTRAINT `2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`),
  CONSTRAINT `check_cantidad_pedido_positiva` CHECK (`cantidad` > 0),
  CONSTRAINT `check_subtotal_pedido_no_negativo` CHECK (`subtotal` >= 0)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `detalle_produccion`
--

DROP TABLE IF EXISTS `detalle_produccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_produccion` (
  `id_detalle` int(11) NOT NULL AUTO_INCREMENT,
  `cantidad` float NOT NULL,
  `id_produccion` int(11) NOT NULL,
  `id_materia` int(11) DEFAULT NULL,
  `id_producto` int(11) NOT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `id_produccion` (`id_produccion`),
  KEY `id_materia` (`id_materia`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `1` FOREIGN KEY (`id_produccion`) REFERENCES `producciones` (`id_produccion`),
  CONSTRAINT `2` FOREIGN KEY (`id_materia`) REFERENCES `materias_primas` (`id_materia`),
  CONSTRAINT `3` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `detalle_venta`
--

DROP TABLE IF EXISTS `detalle_venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_venta` (
  `id_detalle` int(11) NOT NULL AUTO_INCREMENT,
  `cantidad` int(11) NOT NULL,
  `subtotal` float NOT NULL,
  `id_venta` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `id_venta` (`id_venta`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `1` FOREIGN KEY (`id_venta`) REFERENCES `ventas` (`id_venta`),
  CONSTRAINT `2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`),
  CONSTRAINT `check_cantidad_venta_positiva` CHECK (`cantidad` > 0),
  CONSTRAINT `check_subtotal_venta_no_negativo` CHECK (`subtotal` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `empleados`
--

DROP TABLE IF EXISTS `empleados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `empleados` (
  `id_empleado` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `id_persona` int(11) NOT NULL,
  PRIMARY KEY (`id_empleado`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_persona` (`id_persona`),
  CONSTRAINT `1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `2` FOREIGN KEY (`id_persona`) REFERENCES `personas` (`id_persona`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventario_terminado`
--

DROP TABLE IF EXISTS `inventario_terminado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventario_terminado` (
  `id_inventario` int(11) NOT NULL AUTO_INCREMENT,
  `id_producto` int(11) NOT NULL,
  `cantidad_disponible` int(11) NOT NULL,
  `fecha_actualizacion` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_inventario`),
  UNIQUE KEY `id_producto` (`id_producto`),
  CONSTRAINT `1` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`),
  CONSTRAINT `check_inventario_terminado_no_negativo` CHECK (`cantidad_disponible` >= 0)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `materias_primas`
--

DROP TABLE IF EXISTS `materias_primas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `materias_primas` (
  `id_materia` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `unidad_medida` varchar(20) NOT NULL,
  `stock_actual` float NOT NULL,
  `stock_minimo` float NOT NULL,
  `precio` float NOT NULL,
  `porcentaje_merma` float NOT NULL,
  `factor_conversion` float NOT NULL,
  `estado` tinyint(1) DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL,
  `id_categoria_ingrediente` int(11) NOT NULL,
  `id_proveedor` int(11) NOT NULL,
  PRIMARY KEY (`id_materia`),
  UNIQUE KEY `nombre` (`nombre`),
  KEY `id_proveedor` (`id_proveedor`),
  KEY `fk_materias_primas_categoria_ingrediente` (`id_categoria_ingrediente`),
  CONSTRAINT `1` FOREIGN KEY (`id_categoria_ingrediente`) REFERENCES `categorias_ingrediente` (`id_categoria_ingrediente`),
  CONSTRAINT `2` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id_proveedor`),
  CONSTRAINT `fk_materias_primas_categoria_ingrediente` FOREIGN KEY (`id_categoria_ingrediente`) REFERENCES `categorias_ingrediente` (`id_categoria_ingrediente`),
  CONSTRAINT `check_stock_actual_materia_no_negativo` CHECK (`stock_actual` >= 0),
  CONSTRAINT `check_stock_minimo_materia_no_negativo` CHECK (`stock_minimo` >= 0),
  CONSTRAINT `check_porcentaje_merma` CHECK (`porcentaje_merma` >= 0 and `porcentaje_merma` <= 100),
  CONSTRAINT `check_factor_conversion_positivo` CHECK (`factor_conversion` > 0),
  CONSTRAINT `check_unidad_medida_materia` CHECK (`unidad_medida` in ('kg','g','l','ml','pz'))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mermas`
--

DROP TABLE IF EXISTS `mermas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `mermas` (
  `id_merma` int(11) NOT NULL AUTO_INCREMENT,
  `tipo_origen` varchar(30) DEFAULT NULL,
  `id_materia` int(11) DEFAULT NULL,
  `id_inventario` int(11) DEFAULT NULL,
  `id_producto` int(11) DEFAULT NULL,
  `cantidad` double NOT NULL,
  `costo_unitario` float DEFAULT NULL,
  `costo_perdida` double NOT NULL,
  `motivo` varchar(50) NOT NULL,
  `observaciones` text DEFAULT NULL,
  `autorizada` tinyint(1) DEFAULT NULL,
  `id_usuario_registro` int(11) DEFAULT NULL,
  `id_usuario_autorizacion` int(11) DEFAULT NULL,
  `fecha` datetime DEFAULT NULL,
  `tipo_articulo` varchar(50) DEFAULT NULL,
  `articulo_id` int(11) NOT NULL,
  `fecha_registro` datetime DEFAULT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_merma`),
  KEY `fk_merma_materia` (`id_materia`),
  KEY `fk_merma_inventario` (`id_inventario`),
  KEY `fk_merma_producto` (`id_producto`),
  KEY `fk_merma_usuario_autorizacion` (`id_usuario_autorizacion`),
  KEY `idx_mermas_fecha` (`fecha`),
  KEY `idx_mermas_motivo` (`motivo`),
  KEY `idx_mermas_tipo_origen` (`tipo_origen`),
  KEY `idx_mermas_usuario` (`id_usuario_registro`),
  CONSTRAINT `fk_merma_inventario` FOREIGN KEY (`id_inventario`) REFERENCES `inventario_terminado` (`id_inventario`),
  CONSTRAINT `fk_merma_materia` FOREIGN KEY (`id_materia`) REFERENCES `materias_primas` (`id_materia`),
  CONSTRAINT `fk_merma_producto` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`),
  CONSTRAINT `fk_merma_usuario_autorizacion` FOREIGN KEY (`id_usuario_autorizacion`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `fk_merma_usuario_registro` FOREIGN KEY (`id_usuario_registro`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `check_merma_tipo_origen` CHECK (`tipo_origen` in ('MateriaPrima','InventarioTerminado')),
  CONSTRAINT `check_merma_cantidad` CHECK (`cantidad` > 0),
  CONSTRAINT `check_merma_costo_unitario` CHECK (`costo_unitario` >= 0),
  CONSTRAINT `check_merma_costo_perdida` CHECK (`costo_perdida` >= 0)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `movimientos_caja`
--

DROP TABLE IF EXISTS `movimientos_caja`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimientos_caja` (
  `id_movimiento` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL,
  `tipo` varchar(20) NOT NULL,
  `monto` float NOT NULL,
  `descripcion` text DEFAULT NULL,
  `id_caja` int(11) NOT NULL,
  PRIMARY KEY (`id_movimiento`),
  KEY `id_caja` (`id_caja`),
  CONSTRAINT `1` FOREIGN KEY (`id_caja`) REFERENCES `caja` (`id_caja`),
  CONSTRAINT `check_tipo_movimiento` CHECK (`tipo` in ('Ingreso','Egreso')),
  CONSTRAINT `check_monto_movimiento_no_negativo` CHECK (`monto` >= 0)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pedidos`
--

DROP TABLE IF EXISTS `pedidos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedidos` (
  `id_pedido` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL,
  `fecha_entrega` datetime DEFAULT NULL,
  `estado` varchar(50) NOT NULL,
  `id_cliente` int(11) NOT NULL,
  `requiere_produccion` tinyint(1) DEFAULT NULL,
  `total` float NOT NULL,
  `estado_pago` varchar(50) NOT NULL DEFAULT 'Pendiente',
  PRIMARY KEY (`id_pedido`),
  KEY `fk_pedidos_clientes` (`id_cliente`),
  CONSTRAINT `1` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`),
  CONSTRAINT `fk_pedidos_clientes` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`),
  CONSTRAINT `check_estado_pedido` CHECK (`estado` in ('Pendiente','En Proceso','Producido','Completado','Cancelado')),
  CONSTRAINT `check_total_pedido_no_negativo` CHECK (`total` >= 0)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pedidos_meta`
--

DROP TABLE IF EXISTS `pedidos_meta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedidos_meta` (
  `id_pedido` int(11) NOT NULL,
  `metodo_pago` varchar(50) NOT NULL,
  `tarjeta_titular` varchar(120) DEFAULT NULL,
  `tarjeta_ultimos4` varchar(4) DEFAULT NULL,
  `tarjeta_vencimiento` varchar(5) DEFAULT NULL,
  `id_usuario` int(11) NOT NULL,
  PRIMARY KEY (`id_pedido`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `1` FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id_pedido`),
  CONSTRAINT `2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `check_metodo_pago_pedido_meta` CHECK (`metodo_pago` in ('Efectivo','Tarjeta','Transferencia'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `personas`
--

DROP TABLE IF EXISTS `personas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `personas` (
  `id_persona` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `apellido_p` varchar(50) NOT NULL,
  `apellido_m` varchar(50) DEFAULT NULL,
  `telefono` varchar(10) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `rfc_tax_id` varchar(20) DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL,
  PRIMARY KEY (`id_persona`),
  UNIQUE KEY `telefono` (`telefono`),
  UNIQUE KEY `correo` (`correo`),
  KEY `idx_personas_nombre` (`nombre`,`apellido_p`,`apellido_m`),
  KEY `idx_personas_contacto` (`telefono`,`correo`),
  KEY `idx_personas_rfc` (`rfc_tax_id`),
  CONSTRAINT `check_telefono` CHECK (`telefono` regexp '^[0-9]{10}$'),
  CONSTRAINT `check_correo_empleado` CHECK (`correo` regexp '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,}$')
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `producciones`
--

DROP TABLE IF EXISTS `producciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `producciones` (
  `id_produccion` int(11) NOT NULL AUTO_INCREMENT,
  `fecha_solicitud` datetime NOT NULL,
  `fecha_completada` datetime DEFAULT NULL,
  `fecha_necesaria` datetime NOT NULL,
  `estado` varchar(50) NOT NULL,
  `id_pedido` int(11) DEFAULT NULL,
  `id_usuario` int(11) NOT NULL,
  `fecha_creacion` datetime NOT NULL,
  PRIMARY KEY (`id_produccion`),
  KEY `id_pedido` (`id_pedido`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `1` FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id_pedido`),
  CONSTRAINT `2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `check_estado_produccion` CHECK (`estado` in ('Solicitada','En Proceso','Completada'))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `id_producto` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `precio` float NOT NULL,
  `stock_minimo` float NOT NULL,
  `imagen` varchar(255) DEFAULT NULL,
  `estado` tinyint(1) DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL,
  `id_categoria_platillo` int(11) NOT NULL,
  `fecha_produccion` datetime DEFAULT NULL,
  `dias_duracion` int(11) NOT NULL DEFAULT 2,
  `fecha_merma` datetime DEFAULT NULL,
  PRIMARY KEY (`id_producto`),
  UNIQUE KEY `nombre` (`nombre`),
  KEY `fk_productos_categoria_platillo` (`id_categoria_platillo`),
  CONSTRAINT `1` FOREIGN KEY (`id_categoria_platillo`) REFERENCES `categorias_platillo` (`id_categoria_platillo`),
  CONSTRAINT `fk_productos_categoria_platillo` FOREIGN KEY (`id_categoria_platillo`) REFERENCES `categorias_platillo` (`id_categoria_platillo`),
  CONSTRAINT `check_precio_producto_no_negativo` CHECK (`precio` >= 0),
  CONSTRAINT `check_stock_minimo_producto_no_negativo` CHECK (`stock_minimo` >= 0),
  CONSTRAINT `check_formato_imagen` CHECK (`imagen` regexp '^((https?://.*.(png|jpg|jpeg|gif|svg|webp))|(uploads/.*.(png|jpg|jpeg|gif|svg|webp)))$'),
  CONSTRAINT `check_dias_duracion_producto_minimo` CHECK (`dias_duracion` >= 2)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proveedores`
--

DROP TABLE IF EXISTS `proveedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedores` (
  `id_proveedor` int(11) NOT NULL AUTO_INCREMENT,
  `id_persona` int(11) NOT NULL,
  `id_categoria_proveedor` int(11) NOT NULL,
  `estado` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id_proveedor`),
  KEY `id_persona` (`id_persona`),
  KEY `fk_proveedores_categoria_proveedor` (`id_categoria_proveedor`),
  CONSTRAINT `1` FOREIGN KEY (`id_persona`) REFERENCES `personas` (`id_persona`),
  CONSTRAINT `2` FOREIGN KEY (`id_categoria_proveedor`) REFERENCES `categorias_proveedor` (`id_categoria_proveedor`),
  CONSTRAINT `fk_proveedores_categoria_proveedor` FOREIGN KEY (`id_categoria_proveedor`) REFERENCES `categorias_proveedor` (`id_categoria_proveedor`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `receta_detalle`
--

DROP TABLE IF EXISTS `receta_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `receta_detalle` (
  `id_detalle` int(11) NOT NULL AUTO_INCREMENT,
  `cantidad` float NOT NULL,
  `id_receta` int(11) NOT NULL,
  `id_materia` int(11) NOT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `id_receta` (`id_receta`),
  KEY `id_materia` (`id_materia`),
  CONSTRAINT `1` FOREIGN KEY (`id_receta`) REFERENCES `recetas` (`id_receta`),
  CONSTRAINT `2` FOREIGN KEY (`id_materia`) REFERENCES `materias_primas` (`id_materia`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `recetas`
--

DROP TABLE IF EXISTS `recetas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `recetas` (
  `id_receta` int(11) NOT NULL AUTO_INCREMENT,
  `id_producto` int(11) NOT NULL,
  `rendimiento` float NOT NULL,
  `nota` text DEFAULT NULL,
  `estado` tinyint(1) DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL,
  `porciones` int(11) NOT NULL DEFAULT 1,
  `rendimiento_porciones` int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_receta`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `1` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`),
  CONSTRAINT `check_receta_porciones_positivas` CHECK (`porciones` > 0)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id_rol` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id_rol`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `contrasena` text NOT NULL,
  `estado` tinyint(1) DEFAULT NULL,
  `fs_uniquifier` varchar(255) NOT NULL,
  `fecha_creacion` datetime NOT NULL,
  `id_rol` int(11) NOT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `fs_uniquifier` (`fs_uniquifier`),
  KEY `id_rol` (`id_rol`),
  CONSTRAINT `1` FOREIGN KEY (`id_rol`) REFERENCES `roles` (`id_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `v_clientes`
--

DROP TABLE IF EXISTS `v_clientes`;
/*!50001 DROP VIEW IF EXISTS `v_clientes`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `v_clientes` AS SELECT
 1 AS `id_cliente`,
  1 AS `id_usuario`,
  1 AS `username`,
  1 AS `estado`,
  1 AS `nombre`,
  1 AS `apellido_p`,
  1 AS `apellido_m`,
  1 AS `telefono`,
  1 AS `correo` */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `v_empleados`
--

DROP TABLE IF EXISTS `v_empleados`;
/*!50001 DROP VIEW IF EXISTS `v_empleados`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
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
  1 AS `correo` */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `v_materias_primas`
--

DROP TABLE IF EXISTS `v_materias_primas`;
/*!50001 DROP VIEW IF EXISTS `v_materias_primas`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
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
  1 AS `id_proveedor` */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `v_productos`
--

DROP TABLE IF EXISTS `v_productos`;
/*!50001 DROP VIEW IF EXISTS `v_productos`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `v_productos` AS SELECT
 1 AS `id_producto`,
  1 AS `nombre`,
  1 AS `descripcion`,
  1 AS `precio`,
  1 AS `stock_actual`,
  1 AS `stock_minimo`,
  1 AS `imagen`,
  1 AS `estado`,
  1 AS `categoria` */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `v_proveedores`
--

DROP TABLE IF EXISTS `v_proveedores`;
/*!50001 DROP VIEW IF EXISTS `v_proveedores`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `v_proveedores` AS SELECT
 1 AS `id_proveedor`,
  1 AS `nombre`,
  1 AS `apellido_p`,
  1 AS `apellido_m`,
  1 AS `telefono`,
  1 AS `correo`,
  1 AS `estado` */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `ventas`
--

DROP TABLE IF EXISTS `ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas` (
  `id_venta` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL,
  `total` float NOT NULL,
  `metodo_pago` varchar(50) NOT NULL,
  `estado` varchar(50) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `fecha_creacion` datetime NOT NULL,
  PRIMARY KEY (`id_venta`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `check_estado_venta` CHECK (`estado` in ('Pendiente','Completada','Cancelada')),
  CONSTRAINT `check_metodo_pago_venta` CHECK (`metodo_pago` in ('Efectivo','Tarjeta','Transferencia')),
  CONSTRAINT `check_total_venta_no_negativo` CHECK (`total` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping events for database 'fonda'
--

--
-- Dumping routines for database 'fonda'
--
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_activarCategoria` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_activarMateriaPrima` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_activarProveedor` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_activarUsuario` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_actualizarCategoria` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_actualizarMateriaPrima` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_actualizarMiCuenta` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_actualizarMiCuenta`(
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
                END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_actualizarProveedor` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_actualizarUsuario` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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

    
    SELECT COALESCE(c.id_persona, e.id_persona)
    INTO v_id_persona
    FROM usuarios u
    LEFT JOIN clientes c ON c.id_usuario = u.id_usuario
    LEFT JOIN empleados e ON e.id_usuario = u.id_usuario
    WHERE u.id_usuario = p_id_usuario;

    
    
    
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_crearCategoria` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_crearCliente` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_crearCliente`(
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
                END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_crearEmpleado` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
    IN p_rol VARCHAR(50) 
)
BEGIN
    DECLARE v_id_persona INT;
    DECLARE v_id_usuario INT;
    DECLARE v_id_rol INT;

    
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

    
    SELECT id_rol INTO v_id_rol
    FROM roles
    WHERE nombre = p_rol
    LIMIT 1;

    IF v_id_rol IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Rol no valido';
    END IF;

    
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

    
    INSERT INTO usuarios(
        username, contrasena, estado,
        fs_uniquifier, fecha_creacion, id_rol
    )
    VALUES (
        p_username, p_password, TRUE,
        UUID(), NOW(), v_id_rol
    );

    SET v_id_usuario = LAST_INSERT_ID();

    
    INSERT INTO empleados(id_usuario, id_persona)
    VALUES (v_id_usuario, v_id_persona);

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_crearIngrediente` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_crearMateriaPrima` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_crearProducto` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_crearProveedor` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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

    
    IF EXISTS (
        SELECT 1 FROM personas 
        WHERE correo = p_correo OR telefono = p_telefono
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Correo o telefono ya existen';
    END IF;
    
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

    
    INSERT INTO proveedores(id_persona, estado)
    VALUES (v_id_persona,1);

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_desactivarUsuario` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_eliminarCategoria` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_eliminarMateriaPrima` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_eliminarProveedor` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_eliminarUsuario` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_filtrarCategorias` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_filtrarMaterias` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_filtrarProveedores` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_filtrarUsuarios` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_insertarUsuario` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_obtenerCategoria` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_obtenerMateriaPrima` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_obtenerUsuario` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_reactivarEmpleado` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_reactivarUsuario` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_verMiCuenta` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
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
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_verProveedores` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_verProveedores`()
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
    LEFT JOIN personas p ON p.id_persona = pr.id_persona;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_verUsuarios` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_verUsuarios`()
BEGIN
    SELECT 
        u.id_usuario,            
        u.username,              
        u.estado,                
        p.nombre,                
        p.apellido_p,            
        p.apellido_m,            
        r.nombre AS rol_nombre 	 
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
-- Final view structure for view `v_clientes`
--

/*!50001 DROP VIEW IF EXISTS `v_clientes`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb3_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_clientes` AS select 1 AS `id_cliente`,1 AS `id_usuario`,1 AS `username`,1 AS `estado`,1 AS `nombre`,1 AS `apellido_p`,1 AS `apellido_m`,1 AS `telefono`,1 AS `correo` */;
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
/*!50001 SET collation_connection      = utf8mb3_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_empleados` AS select 1 AS `id_empleado`,1 AS `id_usuario`,1 AS `username`,1 AS `estado`,1 AS `rol`,1 AS `nombre`,1 AS `apellido_p`,1 AS `apellido_m`,1 AS `telefono`,1 AS `correo` */;
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
/*!50001 SET collation_connection      = utf8mb3_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_materias_primas` AS select 1 AS `id_materia`,1 AS `nombre`,1 AS `unidad_medida`,1 AS `stock_actual`,1 AS `stock_minimo`,1 AS `porcentaje_merma`,1 AS `factor_conversion`,1 AS `estado`,1 AS `categoria`,1 AS `id_proveedor` */;
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
/*!50001 SET collation_connection      = utf8mb3_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_productos` AS select 1 AS `id_producto`,1 AS `nombre`,1 AS `descripcion`,1 AS `precio`,1 AS `stock_actual`,1 AS `stock_minimo`,1 AS `imagen`,1 AS `estado`,1 AS `categoria` */;
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
/*!50001 SET collation_connection      = utf8mb3_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_proveedores` AS select 1 AS `id_proveedor`,1 AS `nombre`,1 AS `apellido_p`,1 AS `apellido_m`,1 AS `telefono`,1 AS `correo`,1 AS `estado` */;
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
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-04-16 10:53:43
