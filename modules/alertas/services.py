from models import db, MateriaPrima, Producto, Compra, DetalleCompra, Pedido, Produccion


def construir_contexto_alertas(user):
    alertas_materias = []
    alertas_productos = []
    alertas_pedidos_cliente = []
    alertas_compras_solicitadas = []
    alertas_producciones_solicitadas = []
    total_alertas = 0

    if not user.is_authenticated:
        return {
            'current_user': user,
            'alertas_materias': alertas_materias,
            'alertas_productos': alertas_productos,
            'alertas_pedidos_cliente': alertas_pedidos_cliente,
            'alertas_compras_solicitadas': alertas_compras_solicitadas,
            'alertas_producciones_solicitadas': alertas_producciones_solicitadas,
            'alertas_stock_total': total_alertas,
            'alertas_total': total_alertas,
        }

    if user.id_rol == 1:
        materias_bajas = (
            MateriaPrima.query
            .filter(MateriaPrima.stock_actual <= MateriaPrima.stock_minimo)
            .order_by(MateriaPrima.nombre.asc())
            .all()
        )

        ids_materias_bajas = [m.id_materia for m in materias_bajas]
        ids_materias_solicitadas = set()

        if ids_materias_bajas:
            filas_solicitadas = (
                db.session.query(DetalleCompra.id_materia)
                .join(Compra, Compra.id_compra == DetalleCompra.id_compra)
                .filter(
                    Compra.estado.in_(['Solicitada', 'En Camino']),
                    DetalleCompra.id_materia.in_(ids_materias_bajas)
                )
                .distinct()
                .all()
            )
            ids_materias_solicitadas = {fila[0] for fila in filas_solicitadas}

        alertas_materias = [
            {
                'id': m.id_materia,
                'nombre': m.nombre,
                'stock_actual': m.stock_actual,
                'stock_minimo': m.stock_minimo,
                'unidad_medida': m.unidad_medida,
                'compra_solicitada': m.id_materia in ids_materias_solicitadas,
            }
            for m in materias_bajas
        ]

        productos_bajos = (
            Producto.query
            .filter(Producto.stock_actual <= Producto.stock_minimo)
            .order_by(Producto.nombre.asc())
            .all()
        )
        alertas_productos = [
            {
                'id': p.id_producto,
                'nombre': p.nombre,
                'stock_actual': p.stock_actual,
                'stock_minimo': p.stock_minimo,
            }
            for p in productos_bajos
        ]

        total_alertas = len(alertas_materias) + len(alertas_productos)

    elif user.id_rol == 2:
        producciones_solicitadas = (
            Produccion.query
            .filter(Produccion.estado.in_(['Solicitada', 'En Proceso']))
            .order_by(Produccion.fecha_solicitud.desc())
            .limit(10)
            .all()
        )

        alertas_producciones_solicitadas = [
            {
                'id_produccion': produccion.id_produccion,
                'estado': produccion.estado,
                'fecha_solicitud': produccion.fecha_solicitud,
                'fecha_necesaria': produccion.fecha_necesaria,
                'clave': f"{produccion.id_produccion}:{produccion.estado}",
            }
            for produccion in producciones_solicitadas
        ]
        total_alertas = len(alertas_producciones_solicitadas)

    elif user.id_rol == 3:
        materias_bajas = (
            MateriaPrima.query
            .filter(MateriaPrima.stock_actual <= MateriaPrima.stock_minimo)
            .order_by(MateriaPrima.nombre.asc())
            .all()
        )

        ids_materias_bajas = [m.id_materia for m in materias_bajas]
        ids_materias_solicitadas = set()

        if ids_materias_bajas:
            filas_solicitadas = (
                db.session.query(DetalleCompra.id_materia)
                .join(Compra, Compra.id_compra == DetalleCompra.id_compra)
                .filter(
                    Compra.estado.in_(['Solicitada', 'En Camino']),
                    DetalleCompra.id_materia.in_(ids_materias_bajas)
                )
                .distinct()
                .all()
            )
            ids_materias_solicitadas = {fila[0] for fila in filas_solicitadas}

        alertas_materias = [
            {
                'id': m.id_materia,
                'nombre': m.nombre,
                'stock_actual': m.stock_actual,
                'stock_minimo': m.stock_minimo,
                'unidad_medida': m.unidad_medida,
                'compra_solicitada': m.id_materia in ids_materias_solicitadas,
            }
            for m in materias_bajas
        ]

        compras_solicitadas = (
            Compra.query
            .filter(Compra.estado == 'Solicitada')
            .order_by(Compra.fecha.desc())
            .limit(10)
            .all()
        )
        alertas_compras_solicitadas = [
            {
                'id_compra': compra.id_compra,
                'estado': compra.estado,
                'fecha': compra.fecha,
                'total': compra.total,
                'clave': f"{compra.id_compra}:{compra.estado}",
            }
            for compra in compras_solicitadas
        ]

        productos_bajos = (
            Producto.query
            .filter(Producto.stock_actual <= Producto.stock_minimo)
            .order_by(Producto.nombre.asc())
            .all()
        )
        alertas_productos = [
            {
                'id': p.id_producto,
                'nombre': p.nombre,
                'stock_actual': p.stock_actual,
                'stock_minimo': p.stock_minimo,
            }
            for p in productos_bajos
        ]

        total_alertas = len(alertas_compras_solicitadas) + len(alertas_productos) + len(alertas_materias)

    elif user.id_rol == 4:
        id_cliente = user.cliente.id_cliente if user.cliente else None
        if id_cliente:
            pedidos_actualizados = (
                Pedido.query
                .filter(
                    Pedido.id_cliente == id_cliente,
                    Pedido.estado != 'Pendiente'
                )
                .order_by(Pedido.fecha.desc())
                .limit(10)
                .all()
            )

            alertas_pedidos_cliente = [
                {
                    'id_pedido': p.id_pedido,
                    'estado': p.estado,
                    'fecha': p.fecha,
                    'clave': f"{p.id_pedido}:{p.estado}",
                }
                for p in pedidos_actualizados
            ]
        total_alertas = len(alertas_pedidos_cliente)

    return {
        'current_user': user,
        'alertas_materias': alertas_materias,
        'alertas_productos': alertas_productos,
        'alertas_pedidos_cliente': alertas_pedidos_cliente,
        'alertas_compras_solicitadas': alertas_compras_solicitadas,
        'alertas_producciones_solicitadas': alertas_producciones_solicitadas,
        'alertas_stock_total': total_alertas,
        'alertas_total': total_alertas,
    }


def marcar_alertas_vistas(user, session_obj):
    if user.id_rol == 1:
        materias_bajas = MateriaPrima.query.filter(
            MateriaPrima.stock_actual <= MateriaPrima.stock_minimo
        ).all()
        productos_bajos = Producto.query.filter(
            Producto.stock_actual <= Producto.stock_minimo
        ).all()

        session_obj['alertas_vistas_materias'] = [m.id_materia for m in materias_bajas]
        session_obj['alertas_vistas_productos'] = [p.id_producto for p in productos_bajos]

    elif user.id_rol == 2:
        producciones_solicitadas = Produccion.query.filter(
            Produccion.estado.in_(['Solicitada', 'En Proceso'])
        ).all()
        session_obj['alertas_vistas_producciones'] = [
            f"{p.id_produccion}:{p.estado}" for p in producciones_solicitadas
        ]

    elif user.id_rol == 3:
        # En cajero no ocultamos alertas por sesión.
        session_obj.pop('alertas_vistas_materias', None)
        session_obj.pop('alertas_vistas_compras', None)
        session_obj.pop('alertas_vistas_productos', None)

    elif user.id_rol == 4 and user.cliente:
        pedidos_actualizados = (
            Pedido.query
            .filter(
                Pedido.id_cliente == user.cliente.id_cliente,
                Pedido.estado != 'Pendiente'
            )
            .all()
        )
        session_obj['alertas_vistas_pedidos'] = [
            f"{p.id_pedido}:{p.estado}" for p in pedidos_actualizados
        ]

    session_obj.modified = True