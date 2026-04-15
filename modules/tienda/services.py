from models import db, Producto, Categoria, Carrito, DetalleCarrito, Pedido, DetallePedido, PedidoMeta
from flask_login import current_user
from datetime import datetime
import re
import logging
from utils.product_freshness import aplicar_merma_automatica_productos

logger = logging.getLogger(__name__)

# ===============================
# OBTENER MENÚ
# ===============================
def obtener_menu():
    try:
        aplicar_merma_automatica_productos()

        productos = (
            Producto.query
            .filter(Producto.estado.is_(True), Producto.stock_actual > 0)
            .order_by(Producto.nombre.asc())
            .all()
        )

        resultado = []
        for p in productos:
            resultado.append({
                "id": p.id_producto,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "precio": p.precio,
                "imagen": p.imagen,
                "categoria": p.categoria_platillo.nombre if p.categoria_platillo else "Sin categoria"
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
        aplicar_merma_automatica_productos()

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
def _luhn_valido(numero_tarjeta):
    digitos = [int(d) for d in numero_tarjeta if d.isdigit()]
    checksum = 0
    par = len(digitos) % 2
    for i, d in enumerate(digitos):
        if i % 2 == par:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


def _validar_datos_tarjeta(numero, titular, vencimiento, cvv):
    numero_limpio = re.sub(r'\s+', '', (numero or '').strip())
    titular = (titular or '').strip()
    vencimiento = (vencimiento or '').strip()
    cvv = (cvv or '').strip()

    if not re.fullmatch(r'\d{13,19}', numero_limpio):
        return False, "Número de tarjeta inválido"

    # Permitimos tarjetas de prueba/locales: validamos formato y longitud sin exigir Luhn.

    if len(titular) < 3:
        return False, "Ingresa el nombre del titular"

    if not re.fullmatch(r'(0[1-9]|1[0-2])/\d{2}', vencimiento):
        return False, "Fecha de vencimiento inválida (MM/AA)"

    mes, anio = vencimiento.split('/')
    mes = int(mes)
    anio = 2000 + int(anio)
    hoy = datetime.utcnow()

    if (anio < hoy.year) or (anio == hoy.year and mes < hoy.month):
        return False, "La tarjeta está vencida"

    if not re.fullmatch(r'\d{3,4}', cvv):
        return False, "CVV inválido"

    return True, None


def finalizar_pedido(metodo_pago='Efectivo', datos_tarjeta=None):
    try:
        if not current_user.is_authenticated:
            return False, "Usuario no autenticado"

        metodo_pago = (metodo_pago or '').strip().title()
        if metodo_pago not in ('Efectivo', 'Tarjeta', 'Transferencia'):
            return False, "Selecciona un método de pago válido"

        if metodo_pago == 'Tarjeta':
            datos_tarjeta = datos_tarjeta or {}
            valido, error = _validar_datos_tarjeta(
                datos_tarjeta.get('numero_tarjeta'),
                datos_tarjeta.get('titular_tarjeta'),
                datos_tarjeta.get('vencimiento_tarjeta'),
                datos_tarjeta.get('cvv_tarjeta')
            )
            if not valido:
                return False, error

        tarjeta_titular = None
        tarjeta_ultimos4 = None
        tarjeta_vencimiento = None
        if metodo_pago == 'Tarjeta':
            numero_limpio = re.sub(r'\s+', '', (datos_tarjeta.get('numero_tarjeta') or '').strip())
            tarjeta_titular = (datos_tarjeta.get('titular_tarjeta') or '').strip()
            tarjeta_ultimos4 = numero_limpio[-4:] if len(numero_limpio) >= 4 else None
            tarjeta_vencimiento = (datos_tarjeta.get('vencimiento_tarjeta') or '').strip()

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

        meta = PedidoMeta.query.get(pedido.id_pedido)
        if not meta:
            meta = PedidoMeta(id_pedido=pedido.id_pedido)
            db.session.add(meta)

        meta.metodo_pago = metodo_pago
        meta.tarjeta_titular = tarjeta_titular
        meta.tarjeta_ultimos4 = tarjeta_ultimos4
        meta.tarjeta_vencimiento = tarjeta_vencimiento
        meta.id_usuario = current_user.id_usuario

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
        carrito.metodo_pago = metodo_pago

        db.session.commit()

        return True, "Pedido generado correctamente"

    except Exception as e:
        db.session.rollback()
        return False, str(e)