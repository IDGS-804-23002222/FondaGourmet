import logging
import re
import uuid
from datetime import datetime, timedelta

from flask import current_app
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from werkzeug.security import generate_password_hash

from models import (
    Cliente,
    DetallePedido,
    DetalleProduccion,
    Pedido,
    PedidoMeta,
    Persona,
    Producto,
    Produccion,
    Rol,
    Usuario,
    db,
)
from mongo_models import guardar_log_pedido, guardar_ticket_pedido

logger = logging.getLogger(__name__)

ESTADOS_PAGO_VALIDOS = ('Pendiente', 'Pagado', 'Cancelado')
METODOS_PAGO_VALIDOS = ('Efectivo', 'Tarjeta', 'Transferencia')


def _asegurar_esquema_pedidos():
    return True


def _validar_datos_tarjeta(numero, titular, vencimiento, cvv):
    numero_limpio = re.sub(r'\s+', '', (numero or '').strip())
    titular = (titular or '').strip()
    vencimiento = (vencimiento or '').strip()
    cvv = (cvv or '').strip()

    if not re.fullmatch(r'\d{13,19}', numero_limpio):
        return False, 'Número de tarjeta inválido'

    if len(titular) < 3:
        return False, 'Ingresa el nombre del titular'

    if not re.fullmatch(r'(0[1-9]|1[0-2])/\d{2}', vencimiento):
        return False, 'Fecha de vencimiento inválida (MM/AA)'

    mes, anio = vencimiento.split('/')
    mes = int(mes)
    anio = 2000 + int(anio)
    hoy = datetime.utcnow()

    if (anio < hoy.year) or (anio == hoy.year and mes < hoy.month):
        return False, 'La tarjeta está vencida'

    if not re.fullmatch(r'\d{3,4}', cvv):
        return False, 'CVV inválido'

    return True, None


def _parse_fecha_necesaria(fecha_necesaria):
    valor = (fecha_necesaria or '').strip()
    if not valor:
        return None, None

    formatos = ('%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%d')
    fecha_dt = None
    for fmt in formatos:
        try:
            fecha_dt = datetime.strptime(valor, fmt)
            break
        except ValueError:
            continue

    if not fecha_dt:
        return None, 'Fecha y hora de producción inválida'

    if fecha_dt.date() < datetime.now().date():
        return None, 'La fecha requerida no puede ser menor a hoy'

    return fecha_dt, None


def _obtener_o_crear_cliente_sucursal():
    cliente_sucursal = (
        Cliente.query
        .join(Persona, Persona.id_persona == Cliente.id_persona)
        .filter(func.lower(Persona.nombre) == 'venta en sucursal')
        .first()
    )

    if cliente_sucursal:
        return cliente_sucursal, None

    rol_cliente = Rol.query.filter(func.lower(Rol.nombre) == 'cliente').first()
    if not rol_cliente:
        return None, 'No existe el rol Cliente configurado'

    ts = datetime.utcnow().strftime('%H%M%S%f')
    telefono = ts[-10:]

    persona = Persona(
        nombre='Venta en sucursal',
        apellido_p='Mostrador',
        apellido_m='',
        telefono=telefono,
        correo=f'venta.sucursal.{ts}@local.com',
        direccion='Sucursal',
    )
    db.session.add(persona)
    db.session.flush()

    usuario = Usuario(
        username=f'venta_sucursal_{ts}',
        contrasena=generate_password_hash(uuid.uuid4().hex),
        estado=True,
        fs_uniquifier=str(uuid.uuid4()),
        id_rol=rol_cliente.id_rol,
    )
    db.session.add(usuario)
    db.session.flush()

    cliente = Cliente(
        id_usuario=usuario.id_usuario,
        id_persona=persona.id_persona,
    )
    db.session.add(cliente)
    db.session.flush()

    return cliente, None


def _cliente_nombre(pedido):
    if pedido.cliente and pedido.cliente.persona:
        partes = [
            (pedido.cliente.persona.nombre or '').strip(),
            (pedido.cliente.persona.apellido_p or '').strip(),
            (pedido.cliente.persona.apellido_m or '').strip(),
        ]
        nombre = ' '.join(parte for parte in partes if parte).strip()
        if nombre:
            return nombre
    if pedido.cliente and pedido.cliente.usuario:
        return pedido.cliente.usuario.username or 'Cliente'
    return 'Cliente'


def _serializar_detalles(detalles):
    datos = []
    total = 0.0
    total_items = 0

    for detalle in detalles:
        producto = detalle.producto
        nombre_producto = producto.nombre if producto else f'Producto #{detalle.id_producto}'
        precio_unitario = float(producto.precio or 0) if producto else 0.0
        subtotal = float(detalle.subtotal or (precio_unitario * float(detalle.cantidad or 0)))
        cantidad = int(detalle.cantidad or 0)
        total_items += cantidad
        total += subtotal
        datos.append({
            'id_detalle': detalle.id_detalle,
            'id_producto': detalle.id_producto,
            'nombre': nombre_producto,
            'cantidad': cantidad,
            'precio_unitario': precio_unitario,
            'subtotal': subtotal,
            'atendido': bool(getattr(detalle, 'atendido', False)),
            'en_produccion': bool(getattr(detalle, 'en_produccion', False)),
        })

    return datos, round(total, 2), total_items


def _serializar_pedido(pedido):
    detalles, total_recalculado, total_items = _serializar_detalles(pedido.detalles)
    estado_operativo = (pedido.estado or 'Pendiente').strip().title()
    estado_pago = (pedido.estado_pago or 'Pendiente').strip().title()

    if estado_pago == 'Pagado':
        estado_badge = 'bg-emerald-100 text-emerald-800'
    elif estado_pago == 'Cancelado':
        estado_badge = 'bg-rose-100 text-rose-800'
    else:
        estado_badge = 'bg-amber-100 text-amber-800'

    if estado_operativo in ('Completado', 'Producido'):
        estado_operativo_badge = 'bg-emerald-100 text-emerald-800'
    elif estado_operativo == 'En Proceso':
        estado_operativo_badge = 'bg-cyan-100 text-cyan-800'
    elif estado_operativo == 'Cancelado':
        estado_operativo_badge = 'bg-rose-100 text-rose-800'
    else:
        estado_operativo_badge = 'bg-slate-100 text-slate-800'

    cliente = _cliente_nombre(pedido)
    metodo_pago = pedido.meta_pedido.metodo_pago if pedido.meta_pedido else 'N/D'
    usuario_responsable = pedido.meta_pedido.usuario.username if pedido.meta_pedido and pedido.meta_pedido.usuario else 'N/D'
    fecha_ticket = pedido.fecha.strftime('%d/%m/%Y %H:%M') if pedido.fecha else ''
    fecha_entrega = pedido.fecha_entrega.strftime('%d/%m/%Y %H:%M') if pedido.fecha_entrega else ''

    ticket = {
        'id_pedido': pedido.id_pedido,
        'fecha': fecha_ticket,
        'fecha_entrega': fecha_entrega,
        'cliente': cliente,
        'estado': estado_operativo,
        'estado_pago': estado_pago,
        'metodo_pago': metodo_pago,
        'total': total_recalculado,
        'total_items': total_items,
        'detalles': detalles,
        'usuario_responsable': usuario_responsable,
    }

    return {
        'id_pedido': pedido.id_pedido,
        'fecha': fecha_ticket,
        'fecha_entrega': fecha_entrega,
        'cliente': cliente,
        'cliente_id': pedido.id_cliente,
        'estado': estado_operativo,
        'estado_operativo': estado_operativo,
        'estado_pago': estado_pago,
        'estado_badge': estado_badge,
        'estado_operativo_badge': estado_operativo_badge,
        'metodo_pago': metodo_pago,
        'usuario_responsable': usuario_responsable,
        'usuario_id': pedido.meta_pedido.id_usuario if pedido.meta_pedido else None,
        'requiere_produccion': bool(pedido.requiere_produccion),
        'total': round(float(pedido.total or 0), 2),
        'total_items': total_items,
        'detalles': detalles,
        'ticket': ticket,
        'ticket_json': ticket,
        'ticket_disponible': estado_pago == 'Pagado',
        'calificado': False,
    }


def obtener_pedidos():
    try:
        pedidos_db = (
            Pedido.query
            .options(
                joinedload(Pedido.cliente).joinedload(Cliente.persona),
                joinedload(Pedido.cliente).joinedload(Cliente.usuario),
                joinedload(Pedido.meta_pedido).joinedload(PedidoMeta.usuario),
                joinedload(Pedido.detalles).joinedload(DetallePedido.producto),
            )
            .order_by(Pedido.fecha.desc())
            .all()
        )

        pedidos = [_serializar_pedido(pedido) for pedido in pedidos_db]
        return pedidos, None
    except Exception as e:
        logger.error(f'Error al obtener pedidos: {str(e)}')
        return None, str(e)


def obtener_pedido(id_cliente):
    try:
        if not id_cliente:
            return None, 'ID de cliente no proporcionado.'

        pedidos_db = (
            Pedido.query
            .filter(Pedido.id_cliente == id_cliente)
            .options(
                joinedload(Pedido.cliente).joinedload(Cliente.persona),
                joinedload(Pedido.cliente).joinedload(Cliente.usuario),
                joinedload(Pedido.meta_pedido).joinedload(PedidoMeta.usuario),
                joinedload(Pedido.detalles).joinedload(DetallePedido.producto),
            )
            .order_by(Pedido.fecha.desc())
            .all()
        )

        resultado = []
        for pedido in pedidos_db:
            pedido_data = _serializar_pedido(pedido)
            fecha_estimada = pedido.fecha + timedelta(days=3) if pedido.fecha else None
            pedido_data['id'] = pedido_data['id_pedido']
            pedido_data['fecha_estimada_str'] = fecha_estimada.strftime('%d/%m/%Y') if fecha_estimada else ''
            pedido_data['fecha_str'] = pedido.fecha.strftime('%d/%m/%Y') if pedido.fecha else ''
            pedido_data['fecha_entrega_str'] = pedido.fecha_entrega.strftime('%d/%m/%Y') if pedido.fecha_entrega else ''
            pedido_data['estado_mostrado'] = pedido_data['estado_pago'] if pedido_data['estado_pago'] in ESTADOS_PAGO_VALIDOS else pedido_data['estado']
            resultado.append(pedido_data)

        return resultado, None
    except Exception as e:
        logger.error(f'Error al obtener pedidos: {str(e)}')
        return None, str(e)


def obtener_detalles_pedido(id_pedido):
    try:
        detalles = (
            DetallePedido.query
            .options(joinedload(DetallePedido.producto))
            .filter_by(id_pedido=id_pedido)
            .all()
        )
        resultado = []
        for detalle in detalles:
            resultado.append({
                'id': detalle.id_detalle,
                'id_pedido': detalle.id_pedido,
                'id_producto': detalle.id_producto,
                'nombre': detalle.producto.nombre if detalle.producto else f'Producto #{detalle.id_producto}',
                'cantidad': int(detalle.cantidad or 0),
                'precio_unitario': float(detalle.producto.precio or 0) if detalle.producto else 0.0,
                'subtotal': float(detalle.subtotal or 0),
                'atendido': bool(getattr(detalle, 'atendido', False)),
                'en_produccion': bool(getattr(detalle, 'en_produccion', False)),
            })
        return resultado, None
    except Exception as e:
        logger.error(f'Error al obtener detalles del pedido: {str(e)}')
        return None, str(e)


def crear_pedido_manual(id_cliente, productos, metodo_pago, id_usuario, datos_tarjeta=None, fecha_necesaria=None):
    try:
        if not id_cliente:
            cliente_sucursal, error_cliente = _obtener_o_crear_cliente_sucursal()
            if error_cliente:
                return False, error_cliente
            id_cliente = cliente_sucursal.id_cliente

        if not productos:
            return False, 'Debes agregar al menos un producto'

        metodo_pago = (metodo_pago or '').strip().title()
        if metodo_pago not in METODOS_PAGO_VALIDOS:
            return False, 'Selecciona un método de pago válido'

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

        detalles = []
        total = 0.0

        for item in productos:
            id_producto = item.get('id_producto')
            cantidad = item.get('cantidad')

            if not id_producto or not cantidad:
                return False, 'Cada renglón debe tener producto y cantidad'

            try:
                id_producto = int(id_producto)
                cantidad = int(cantidad)
            except (TypeError, ValueError):
                return False, 'Los datos del pedido son inválidos'

            if cantidad <= 0:
                return False, 'La cantidad debe ser mayor a cero'

            producto = Producto.query.get(id_producto)
            if not producto or not producto.estado:
                return False, f'Producto inválido: {id_producto}'

            subtotal = float(producto.precio or 0) * cantidad
            total += subtotal

            detalles.append({
                'id_producto': id_producto,
                'cantidad': cantidad,
                'subtotal': subtotal,
            })

        pedido = Pedido(
            id_cliente=int(id_cliente),
            total=total,
            fecha=datetime.utcnow(),
            fecha_entrega=None,
            estado='Pendiente',
            estado_pago='Pendiente',
        )
        db.session.add(pedido)
        db.session.flush()

        meta = PedidoMeta(
            id_pedido=pedido.id_pedido,
            metodo_pago=metodo_pago,
            tarjeta_titular=tarjeta_titular,
            tarjeta_ultimos4=tarjeta_ultimos4,
            tarjeta_vencimiento=tarjeta_vencimiento,
            id_usuario=id_usuario,
        )
        db.session.add(meta)

        for detalle in detalles:
            db.session.add(DetallePedido(
                id_pedido=pedido.id_pedido,
                id_producto=detalle['id_producto'],
                cantidad=detalle['cantidad'],
                subtotal=detalle['subtotal'],
                atendido=False,
                en_produccion=False,
            ))

        db.session.commit()
        return True, 'Pedido creado correctamente'

    except Exception as e:
        db.session.rollback()
        logger.error(f'Error al crear pedido manual: {str(e)}')
        return False, str(e)


def procesar_pago_pedido(id_pedido, id_usuario, metodo_pago=None, datos_tarjeta=None):
    try:
        pedido = (
            Pedido.query
            .options(
                joinedload(Pedido.cliente).joinedload(Cliente.persona),
                joinedload(Pedido.meta_pedido).joinedload(PedidoMeta.usuario),
                joinedload(Pedido.detalles).joinedload(DetallePedido.producto),
            )
            .get(id_pedido)
        )
        if not pedido:
            return False, 'Pedido no encontrado'

        if (pedido.estado or '').strip().lower() == 'cancelado':
            return False, 'No se puede cobrar un pedido cancelado'

        if (pedido.estado_pago or '').strip().lower() == 'pagado':
            return False, 'El pedido ya fue pagado'

        metodo_pago = (metodo_pago or (pedido.meta_pedido.metodo_pago if pedido.meta_pedido else '') or '').strip().title()
        if metodo_pago not in METODOS_PAGO_VALIDOS:
            return False, 'Selecciona un método de pago válido'

        tarjeta_titular = None
        tarjeta_ultimos4 = None
        tarjeta_vencimiento = None
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

            numero_limpio = re.sub(r'\s+', '', (datos_tarjeta.get('numero_tarjeta') or '').strip())
            tarjeta_titular = (datos_tarjeta.get('titular_tarjeta') or '').strip()
            tarjeta_ultimos4 = numero_limpio[-4:] if len(numero_limpio) >= 4 else None
            tarjeta_vencimiento = (datos_tarjeta.get('vencimiento_tarjeta') or '').strip()

        if not pedido.meta_pedido:
            pedido.meta_pedido = PedidoMeta(id_pedido=pedido.id_pedido, metodo_pago=metodo_pago, id_usuario=id_usuario)

        pedido.meta_pedido.metodo_pago = metodo_pago
        pedido.meta_pedido.tarjeta_titular = tarjeta_titular
        pedido.meta_pedido.tarjeta_ultimos4 = tarjeta_ultimos4
        pedido.meta_pedido.tarjeta_vencimiento = tarjeta_vencimiento
        pedido.meta_pedido.id_usuario = id_usuario
        pedido.estado_pago = 'Pagado'

        db.session.commit()

        detalles_ticket = []
        for detalle in pedido.detalles:
            detalles_ticket.append({
                'id_producto': detalle.id_producto,
                'nombre': detalle.producto.nombre if detalle.producto else f'Producto #{detalle.id_producto}',
                'cantidad': int(detalle.cantidad or 0),
                'precio_unitario': float(detalle.producto.precio or 0) if detalle.producto else 0.0,
                'subtotal': float(detalle.subtotal or 0),
            })

        guardar_ticket_pedido(current_app, pedido, detalles_ticket, id_usuario)
        guardar_log_pedido(
            current_app,
            'pago_pedido',
            pedido,
            id_usuario,
            pedido.total,
            {'metodo_pago': metodo_pago},
        )

        return True, 'Pedido pagado correctamente'
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error al procesar pago del pedido: {str(e)}')
        return False, str(e)


def cancelar_pedido(id_pedido, id_usuario=None):
    try:
        pedido = Pedido.query.get(id_pedido)
        if not pedido:
            return False, 'Pedido no encontrado'

        estado = (pedido.estado or '').strip().lower()
        estado_pago = (pedido.estado_pago or '').strip().lower()

        if estado == 'cancelado' or estado_pago == 'cancelado':
            return False, 'El pedido ya está cancelado'

        if estado_pago == 'pagado':
            return False, 'No se puede cancelar un pedido ya pagado'

        if estado in ('completado', 'producido'):
            return False, 'No se puede cancelar un pedido ya atendido'

        pedido.estado = 'Cancelado'
        pedido.estado_pago = 'Cancelado'
        db.session.commit()

        guardar_log_pedido(current_app, 'cancelar_pedido', pedido, id_usuario, pedido.total)
        return True, 'Pedido cancelado'
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error al cancelar pedido: {str(e)}')
        return False, str(e)


def editar_pedido_propio(id_pedido, id_cliente, productos, metodo_pago, id_usuario):
    try:
        pedido = Pedido.query.get(id_pedido)

        if not pedido:
            return False, 'Pedido no encontrado'

        if pedido.id_cliente != id_cliente:
            return False, 'No tienes permiso para editar este pedido'

        if pedido.estado != 'Pendiente' or (pedido.estado_pago or 'Pendiente') != 'Pendiente':
            return False, 'Solo puedes editar pedidos pendientes'

        metodo_pago = (metodo_pago or '').strip().title()
        if metodo_pago not in METODOS_PAGO_VALIDOS:
            return False, 'Selecciona un método de pago válido'

        detalles = []
        total = 0.0

        for item in productos:
            id_producto = item.get('id_producto')
            cantidad = item.get('cantidad')

            if not id_producto or not cantidad:
                return False, 'Cada renglón debe tener producto y cantidad'

            try:
                id_producto = int(id_producto)
                cantidad = int(cantidad)
            except (TypeError, ValueError):
                return False, 'Los datos del pedido son inválidos'

            if cantidad <= 0:
                return False, 'La cantidad debe ser mayor a cero'

            producto = Producto.query.get(id_producto)
            if not producto or not producto.estado:
                return False, f'Producto inválido: {id_producto}'

            subtotal = float(producto.precio or 0) * cantidad
            total += subtotal

            detalles.append({
                'id_producto': id_producto,
                'cantidad': cantidad,
                'subtotal': subtotal,
            })

        if not detalles:
            return False, 'Debes agregar al menos un producto'

        DetallePedido.query.filter_by(id_pedido=pedido.id_pedido).delete(synchronize_session=False)

        for detalle in detalles:
            db.session.add(DetallePedido(
                id_pedido=pedido.id_pedido,
                id_producto=detalle['id_producto'],
                cantidad=detalle['cantidad'],
                subtotal=detalle['subtotal'],
                atendido=False,
                en_produccion=False,
            ))

        if not pedido.meta_pedido:
            pedido.meta_pedido = PedidoMeta(id_pedido=pedido.id_pedido, metodo_pago=metodo_pago, id_usuario=id_usuario)
        pedido.meta_pedido.metodo_pago = metodo_pago
        pedido.meta_pedido.id_usuario = id_usuario
        pedido.total = total

        db.session.commit()

        return True, 'Pedido actualizado correctamente'
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error al editar pedido propio: {str(e)}')
        return False, str(e)


def completar_o_producir(id_pedido, id_usuario, fecha_necesaria=None, metodo_pago=None, datos_tarjeta=None):
    try:
        pedido = (
            Pedido.query
            .options(joinedload(Pedido.detalles).joinedload(DetallePedido.producto))
            .get(id_pedido)
        )

        if not pedido:
            return False, 'Pedido no encontrado'

        requerimientos_por_producto = {}
        for detalle in pedido.detalles:
            producto = detalle.producto
            if not producto:
                continue

            item = requerimientos_por_producto.setdefault(
                producto.id_producto,
                {
                    'producto': producto,
                    'cantidad_pedida': 0.0,
                    'stock_actual': float(producto.stock_actual or 0),
                }
            )
            item['cantidad_pedida'] += float(detalle.cantidad or 0)

        faltantes_por_producto = {}
        for id_producto, item in requerimientos_por_producto.items():
            faltante = round(max(0.0, item['cantidad_pedida'] - item['stock_actual']), 2)
            if faltante > 0:
                faltantes_por_producto[id_producto] = {
                    'producto': item['producto'],
                    'faltante': faltante,
                    'cantidad_pedida': item['cantidad_pedida'],
                    'stock_actual': item['stock_actual'],
                }

        necesita_produccion = len(faltantes_por_producto) > 0

        if not necesita_produccion:
            for item in requerimientos_por_producto.values():
                producto = item['producto']
                producto.stock_actual -= item['cantidad_pedida']

            pedido.estado = 'Completado'
            pedido.fecha_entrega = datetime.now()
            pedido.requiere_produccion = False
            db.session.commit()
            return True, 'Pedido completado sin producción'

        fecha_necesaria_dt, error_fecha = _parse_fecha_necesaria(fecha_necesaria)
        if error_fecha:
            return False, error_fecha
        if not fecha_necesaria_dt:
            return False, 'Debes indicar la fecha en que se necesita la producción'

        produccion = Produccion(
            fecha_solicitud=datetime.now(),
            estado='Solicitada',
            fecha_necesaria=fecha_necesaria_dt,
            id_usuario=id_usuario,
            id_pedido=id_pedido,
        )
        db.session.add(produccion)
        db.session.flush()

        for item in faltantes_por_producto.values():
            db.session.add(DetalleProduccion(
                id_produccion=produccion.id_produccion,
                id_producto=item['producto'].id_producto,
                id_materia=None,
                cantidad=item['faltante'],
            ))

        pedido.estado = 'En Proceso'
        pedido.requiere_produccion = True
        db.session.commit()

        return True, 'Se envió a producción'
    except Exception as e:
        db.session.rollback()
        return False, str(e)


def registrar_calificacion_pedido(pedido, id_usuario, calificacion, comentario, productos):
    mongo_db = getattr(current_app, 'mongo', None)
    if mongo_db is None:
        return False, 'No se pudo acceder al almacenamiento de calificaciones'

    if mongo_db.calificaciones_servicio.find_one({'idVenta': pedido.id_pedido}):
        return False, 'Este pedido ya fue calificado y no se puede editar'

    documento = {
        'idVenta': pedido.id_pedido,
        'calificacion': calificacion,
        'comentario': comentario,
        'productos': productos,
        'fecha': datetime.now().strftime('%Y-%m-%d'),
        'id_usuario': id_usuario,
    }
    mongo_db.calificaciones_servicio.insert_one(documento)
    return True, 'Calificación guardada correctamente'
