from models import db, Producto, Categoria, Carrito, DetalleCarrito, Pedido, DetallePedido
from flask import current_app, flash
from flask_login import current_user
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def obtener_menu():
    """Obtiene productos activos para el menú"""
    try:
        productos = Producto.query.filter_by(estado=True).all()

        resultado = []
        for p in productos:
            resultado.append({
                "id": p.id_producto,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "precio": p.precio,
                "imagen": p.imagen  # base64
            })

        return resultado, None

    except Exception as e:
        logger.error(f"Error al obtener menú: {str(e)}")
        return None, str(e)

def obtener_o_crear_carrito():
    try:
        cliente = current_user.cliente
        
        logger.info(f"Obteniendo carrito para cliente: {cliente.id_cliente}")
        carrito = Carrito.query.filter_by(id_cliente=cliente.id_cliente, estado='Abierto').first()

        logger.info(f"Carrito encontrado: {carrito is not None}")
        if not carrito:
            carrito = Carrito(
                id_cliente=cliente.id_cliente,
                total=0,
                fecha_creacion=datetime.utcnow(),
                estado='Abierto'
            )
            db.session.add(carrito)
            db.session.flush()
            logger.info(f"Nuevo carrito creado: {carrito.id_carrito}")
        return carrito, None
    except Exception as e:
        logger.error(f"Error al obtener o crear carrito: {str(e)}")
        return None, str(e)    

def agregar_producto_carrito(id_producto, cantidad = 1):
    try:
        logger.info(f"Agregando producto al carrito: id_producto={id_producto}, cantidad={cantidad}")
        carrito, error = obtener_o_crear_carrito()
        if error:
            logger.error(f"Error al obtener o crear carrito: {str(error)}")
            return False, error
        
        producto = Producto.query.get(id_producto)
        if not producto:
            logger.error(f"Producto no encontrado: {id_producto}")
            return False, "Producto no encontrado"
        elif not producto.estado:
            logger.error(f"Producto no disponible: {id_producto}")  
            return False, "Producto no disponible"
        
        detalle = DetalleCarrito.query.filter_by(
            id_carrito=carrito.id_carrito, 
            id_producto=id_producto
            ).first()

        if detalle:
            cantidad += cantidad
            detalle.subtotal = cantidad * producto.precio
        else:
            detalle = DetalleCarrito(
                id_carrito=carrito.id_carrito,
                id_producto=id_producto,
                cantidad=cantidad,
                subtotal=producto.precio*cantidad
            )
            db.session.add(detalle)
        
        carrito.total = sum(d.subtotal for d in carrito.detalles if d.id_carrito == carrito.id_carrito)
        
        db.session.commit()
        logger.info(f"Producto agregado al carrito: {producto.nombre} (Cantidad: {cantidad})")
        return True, "Producto agregado al carrito"
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al agregar producto al carrito: {str(e)}")
        return False, str(e)
    

        # Obtener cliente
        cliente = usuario.cliente
        if not cliente:
            logger.error(f"Usuario sin cliente asociado: {usuario.id_usuario}")
            return False, "El usuario no tiene cliente asociado"

        # Obtener o crear carrito
        carrito = cliente.carrito
        if not carrito:
            carrito = Carrito(
                id_cliente=cliente.id_cliente,
                total=0
            )
            db.session.add(carrito)
            db.session.flush()  # para obtener ID

        # Buscar si ya existe el producto
        detalle = None
        for d in carrito.detalles:
            if d.id_producto == id_producto:
                detalle = d
                break

        if detalle:
            detalle.cantidad += 1
            detalle.subtotal = detalle.cantidad * producto.precio
        else:
            nuevo_detalle = DetalleCarrito(
                id_producto=id_producto,
                cantidad=1,
                subtotal=producto.precio
            )
            carrito.detalles.append(nuevo_detalle)

        # Recalcular total
        carrito.total = sum(d.subtotal for d in carrito.detalles)

        db.session.commit()
        logger.info("Producto agregado al carrito correctamente")

        return True, "Producto agregado al carrito"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al agregar al carrito: {str(e)}")
        return False, str(e)
    
def obtener_carrito():
    try:
        logger.info(f"Obteniendo carrito para usuario: {current_user.id_usuario}")
        carrito, error = obtener_o_crear_carrito()
        if error:
            logger.error(f"Error al obtener carrito: {str(error)}")
            return None, error

        data = {
            "id": carrito.id_carrito,
            "total": carrito.total,
            "productos": []
        }

        for d in carrito.detalles:
            data["productos"].append({
                "id_detalle": d.id_detalle,
                "producto": d.producto.nombre,
                "precio": d.producto.precio,
                "cantidad": d.cantidad,
                "subtotal": d.subtotal
            })

        logger.info(f"Carrito obtenido: {data}")
        return data, None

    except Exception as e:
        logger.error(f"Error al obtener carrito: {str(e)}")
        return None, str(e)
    

    
def reducir_cantidad_carrito(id_detalle):
    try:
        logger.info(f"Reduciendo cantidad del carrito: id_detalle={id_detalle}")    
        detalle = DetalleCarrito.query.get(id_detalle)
        if not detalle:
            logger.error(f"Detalle de carrito no encontrado: {id_detalle}")
            return False, "Detalle no encontrado"

        carrito = detalle.carrito

        if detalle.cantidad > 1:
            detalle.cantidad -= 1
            detalle.subtotal = detalle.cantidad * detalle.producto.precio
        else:
            db.session.delete(detalle)

        carrito.total = sum(d.subtotal for d in carrito.detalles if d.id_detalle != id_detalle  or detalle.cantidad > 1)

        db.session.commit()
        logger.info(f"Cantidad reducida del carrito: id_detalle={id_detalle}")
        return True, "Cantidad reducida"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al reducir cantidad del carrito: {str(e)}")
        return False, str(e)

def agregar_cantidad_carrito(id_detalle):
    try:
        logger.info(f"Aumentando cantidad del carrito: id_detalle={id_detalle}")    
        detalle = DetalleCarrito.query.get(id_detalle)
        if not detalle:
            logger.error(f"Detalle de carrito no encontrado: {id_detalle}")
            return False, "Detalle no encontrado"

        carrito = detalle.carrito

        detalle.cantidad += 1
        detalle.subtotal = detalle.cantidad * detalle.producto.precio

        carrito.total = sum(d.subtotal for d in carrito.detalles)

        db.session.commit()
        logger.info(f"Cantidad aumentada del carrito: id_detalle={id_detalle}")
        return True, "Cantidad aumentada"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al aumentar cantidad del carrito: {str(e)}")
        return False, str(e)
    
def finalizar_pedido():
    try:
        cliente = current_user.cliente

        # Obtener carrito abierto
        carrito = Carrito.query.filter_by(
            id_cliente=cliente.id_cliente,
            estado='Abierto'
        ).first()

        if not carrito:
            return False, "Carrito no encontrado"

        if not carrito.detalles:
            return False, "El carrito está vacío"

        # Crear pedido
        pedido = Pedido(
            id_cliente=cliente.id_cliente,
            total=carrito.total,
            fecha=datetime.utcnow(),
            estado='Pendiente'
        )
        db.session.add(pedido)
        db.session.flush()  # para obtener ID

        # Pasar productos del carrito al pedido
        for detalle in carrito.detalles:
            detalle_pedido = DetallePedido(
                id_pedido=pedido.id_pedido,
                id_producto=detalle.id_producto,
                cantidad=detalle.cantidad,
                subtotal=detalle.subtotal
            )
            db.session.add(detalle_pedido)

        # Vaciar carrito (opción 1: eliminar detalles)
        for detalle in carrito.detalles:
            db.session.delete(detalle)

        carrito.total = 0

        # (Opcional) cerrar carrito
        carrito.estado = 'Cerrado'

        db.session.commit()

        return True, "Pedido generado correctamente"

    except Exception as e:
        db.session.rollback()
        return False, str(e)
