from models import db, Producto, Categoria, Carrito, DetalleCarrito, Pedido, DetallePedido
from flask_login import current_user
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ===============================
# OBTENER MENÚ
# ===============================
def obtener_menu():
    try:
        productos = Producto.query.filter_by(estado=True).all()

        resultado = []
        for p in productos:
            resultado.append({
                "id": p.id_producto,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "precio": p.precio,
                "imagen": p.imagen
            })

        return resultado, None

    except Exception as e:
        logger.error(f"Error al obtener menú: {str(e)}")
        return None, str(e)


# ===============================
# OBTENER O CREAR CARRITO
# ===============================
def obtener_o_crear_carrito():
    try:
        if not current_user.is_authenticated:
            return None, "Usuario no autenticado"

        cliente = getattr(current_user, "cliente", None)

        if not cliente:
            return None, "Usuario sin cliente asociado"

        carrito = Carrito.query.filter_by(
            id_cliente=cliente.id_cliente,
            estado='Abierto'
        ).first()

        if not carrito:
            carrito = Carrito(
                id_cliente=cliente.id_cliente,
                total=0,
                fecha_creacion=datetime.utcnow(),
                estado='Abierto'
            )
            db.session.add(carrito)
            db.session.flush()

        return carrito, None

    except Exception as e:
        logger.error(f"Error al obtener o crear carrito: {str(e)}")
        return None, str(e)


# ===============================
# AGREGAR PRODUCTO AL CARRITO
# ===============================
def agregar_producto_carrito(id_producto, cantidad=1):
    try:
        carrito, error = obtener_o_crear_carrito()
        if error:
            return False, error

        producto = Producto.query.get(id_producto)

        if not producto:
            return False, "Producto no encontrado"

        if not producto.estado:
            return False, "Producto no disponible"

        detalle = DetalleCarrito.query.filter_by(
            id_carrito=carrito.id_carrito,
            id_producto=id_producto
        ).first()

        if detalle:
            detalle.cantidad += cantidad
            detalle.subtotal = detalle.cantidad * producto.precio
        else:
            detalle = DetalleCarrito(
                id_carrito=carrito.id_carrito,
                id_producto=id_producto,
                cantidad=cantidad,
                subtotal=producto.precio * cantidad
            )
            db.session.add(detalle)

        # Recalcular total correctamente
        carrito.total = sum(d.subtotal for d in carrito.detalles)

        db.session.commit()
        return True, "Producto agregado al carrito"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al agregar producto: {str(e)}")
        return False, str(e)


# ===============================
# OBTENER CARRITO
# ===============================
def obtener_carrito():
    try:
        carrito, error = obtener_o_crear_carrito()
        if error:
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

        return data, None

    except Exception as e:
        logger.error(f"Error al obtener carrito: {str(e)}")
        return None, str(e)


# ===============================
# REDUCIR CANTIDAD
# ===============================
def reducir_cantidad_carrito(id_detalle):
    try:
        detalle = DetalleCarrito.query.get(id_detalle)

        if not detalle:
            return False, "Detalle no encontrado"

        carrito = detalle.carrito

        if detalle.cantidad > 1:
            detalle.cantidad -= 1
            detalle.subtotal = detalle.cantidad * detalle.producto.precio
        else:
            db.session.delete(detalle)

        carrito.total = sum(d.subtotal for d in carrito.detalles)

        db.session.commit()
        return True, "Cantidad reducida"

    except Exception as e:
        db.session.rollback()
        return False, str(e)


# ===============================
# AUMENTAR CANTIDAD
# ===============================
def agregar_cantidad_carrito(id_detalle):
    try:
        detalle = DetalleCarrito.query.get(id_detalle)

        if not detalle:
            return False, "Detalle no encontrado"

        carrito = detalle.carrito

        detalle.cantidad += 1
        detalle.subtotal = detalle.cantidad * detalle.producto.precio

        carrito.total = sum(d.subtotal for d in carrito.detalles)

        db.session.commit()
        return True, "Cantidad aumentada"

    except Exception as e:
        db.session.rollback()
        return False, str(e)


# ===============================
# FINALIZAR PEDIDO
# ===============================
def finalizar_pedido():
    try:
        if not current_user.is_authenticated:
            return False, "Usuario no autenticado"

        cliente = current_user.cliente

        carrito = Carrito.query.filter_by(
            id_cliente=cliente.id_cliente,
            estado='Abierto'
        ).first()

        if not carrito:
            return False, "Carrito no encontrado"

        if not carrito.detalles:
            return False, "El carrito está vacío"

        pedido = Pedido(
            id_cliente=cliente.id_cliente,
            total=carrito.total,
            fecha=datetime.utcnow(),
            fecha_entrega=None,
            estado='Pendiente'
        )
        db.session.add(pedido)
        db.session.flush()

        for detalle in carrito.detalles:
            detalle_pedido = DetallePedido(
                id_pedido=pedido.id_pedido,
                id_producto=detalle.id_producto,
                cantidad=detalle.cantidad,
                subtotal=detalle.subtotal
            )
            db.session.add(detalle_pedido)

        # Vaciar carrito
        for detalle in carrito.detalles:
            db.session.delete(detalle)

        carrito.total = 0
        carrito.estado = 'Cerrado'

        db.session.commit()

        return True, "Pedido generado correctamente"

    except Exception as e:
        db.session.rollback()
        return False, str(e)