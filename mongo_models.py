def guardar_log(app, action, descripcion, id_usuario, ip):
    app.mongo.logs_seguridad.insert_one({
        "fecha": datetime.datetime.utcnow(),
        'accion': action,
        'descripcion': descripcion,
        'id_usuario': id_usuario,
        'ip': request.remote_addr
    })
    
def guardar_ticket(app, venta, detalles):
    app.mongo.tickets.insert_one({
        'id_venta': venta.id_venta,
        'fecha': venta.fecha.strftime('%Y-%m-%d %H:%M:%S'),
        'total': venta.total,
        'id_usuario': venta.id_usuario,
        'detalles': [
            {
                'id_producto': detalle.id_producto,
                'cantidad': detalle.cantidad,
                'precio_unitario': detalle.precio_unitario
            } for detalle in detalles
        ]
    })

def actualizar_dashboard(app):
    resumen_ventas = app.mongo.resumen_ventas.find_one(sort=[("fecha", -1)])
    if not resumen_ventas:
        resumen_ventas = {
            'total_ventas': 0,
            'total_ingresos': 0.0,
            'productos_mas_vendidos': []
        }
    else:
        resumen_ventas['total_ventas'] = Venta.query.count()
        resumen_ventas['total_ingresos'] = db.session.query(db.func.sum(Venta.total)).scalar() or 0.0
        resumen_ventas['productos_mas_vendidos'] = db.session.query(
            DetalleVenta.id_producto,
            db.func.sum(DetalleVenta.cantidad).label('cantidad_total')
        ).group_by(DetalleVenta.id_producto).order_by(db.desc('cantidad_total')).limit(5).all()
    
    app.mongo.dashboard_cache.replace_one({}, resumen_ventas, upsert=True)
    