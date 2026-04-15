import datetime

from models import DetalleVenta, Venta, db


SNAPSHOT_RETENTION_DAYS = 90
SNAPSHOT_RETENTION_SECONDS = SNAPSHOT_RETENTION_DAYS * 24 * 60 * 60


def _ensure_resumen_ventas_ttl_index(app):
    index_name = 'fecha_ttl_90d'
    index_info = app.mongo.resumen_ventas.index_information()

    legacy_index = index_info.get('fecha_1')
    if legacy_index and 'expireAfterSeconds' not in legacy_index:
        app.mongo.resumen_ventas.drop_index('fecha_1')

    app.mongo.resumen_ventas.create_index(
        [('fecha', 1)],
        name=index_name,
        expireAfterSeconds=SNAPSHOT_RETENTION_SECONDS,
    )


def guardar_log(app, action, descripcion, id_usuario, ip):
    if getattr(app, 'mongo', None) is None:
        return False

    app.mongo.logs.insert_one({
        'fecha': datetime.datetime.utcnow(),
        'accion': action,
        'descripcion': descripcion,
        'id_usuario': id_usuario,
        'ip': ip,
    })
    return True


def guardar_ticket(app, venta, detalles):
    if getattr(app, 'mongo', None) is None:
        return False

    app.mongo.tickets.insert_one({
        'id_venta': venta.id_venta,
        'fecha': venta.fecha.strftime('%Y-%m-%d %H:%M:%S') if venta.fecha else datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'total': float(venta.total or 0),
        'id_usuario': venta.id_usuario,
        'detalles': [
            {
                'id_producto': detalle.id_producto,
                'cantidad': float(detalle.cantidad or 0),
                'precio_unitario': float(detalle.precio_unitario or 0),
            }
            for detalle in detalles
        ],
    })
    return True


def guardar_log_pedido(app, accion, pedido, id_usuario, monto, detalle=None):
    if getattr(app, 'mongo', None) is None:
        return False

    documento = {
        'fecha': datetime.datetime.utcnow(),
        'accion': accion,
        'id_pedido': pedido.id_pedido,
        'id_usuario': id_usuario,
        'monto': float(monto or 0),
        'estado_pedido': getattr(pedido, 'estado', None),
        'estado_pago': getattr(pedido, 'estado_pago', None),
    }
    if detalle:
        documento.update(detalle)

    app.mongo.logs.insert_one(documento)
    return True


def guardar_ticket_pedido(app, pedido, detalles, id_usuario):
    if getattr(app, 'mongo', None) is None:
        return False

    cliente_nombre = None
    if pedido.cliente and pedido.cliente.persona:
        partes = [
            (pedido.cliente.persona.nombre or '').strip(),
            (pedido.cliente.persona.apellido_p or '').strip(),
            (pedido.cliente.persona.apellido_m or '').strip(),
        ]
        cliente_nombre = ' '.join(parte for parte in partes if parte).strip() or None

    app.mongo.tickets.insert_one({
        'id_pedido': pedido.id_pedido,
        'fecha': datetime.datetime.utcnow(),
        'fecha_pedido': pedido.fecha,
        'fecha_entrega': pedido.fecha_entrega,
        'id_usuario': id_usuario,
        'cliente': cliente_nombre,
        'estado_pedido': pedido.estado,
        'estado_pago': getattr(pedido, 'estado_pago', None),
        'metodo_pago': pedido.meta_pedido.metodo_pago if pedido.meta_pedido else 'N/D',
        'total': float(pedido.total or 0),
        'detalles': detalles,
    })
    return True


def actualizar_dashboard(app):
    _ensure_resumen_ventas_ttl_index(app)

    productos_mas_vendidos_query = (
        db.session.query(
            DetalleVenta.id_producto,
            db.func.sum(DetalleVenta.cantidad).label('cantidad_total'),
        )
        .group_by(DetalleVenta.id_producto)
        .order_by(db.desc('cantidad_total'))
        .limit(5)
        .all()
    )

    resumen_ventas = {
        'fecha': datetime.datetime.utcnow(),
        'total_ventas': Venta.query.count(),
        'total_ingresos': float(db.session.query(db.func.sum(Venta.total)).scalar() or 0.0),
        'productos_mas_vendidos': [
            {
                'id_producto': row.id_producto,
                'cantidad_total': float(row.cantidad_total or 0),
            }
            for row in productos_mas_vendidos_query
        ],
    }

    app.mongo.resumen_ventas.insert_one(dict(resumen_ventas))
    app.mongo.dashboard_cache.replace_one({}, resumen_ventas, upsert=True)
