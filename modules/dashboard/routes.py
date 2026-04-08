from . import dashboard
from flask import render_template
from flask_login import login_required, current_user
from utils.security import role_required
from models import db, Pedido, DetallePedido, Producto, CategoriaPlatillo
from sqlalchemy import func
from datetime import datetime, timedelta


@dashboard.route('/', methods=['GET', 'POST'])
@login_required
@role_required(1)
def index():
    hoy = datetime.now().date()
    inicio_semana = hoy - timedelta(days=6)
    fecha_operacion = func.coalesce(Pedido.fecha_entrega, Pedido.fecha)

    ventas_hoy_total = db.session.query(func.coalesce(func.sum(Pedido.total), 0)).filter(
        func.date(fecha_operacion) == hoy,
        Pedido.estado == 'Completado'
    ).scalar() or 0

    pedidos_completados_hoy = db.session.query(func.count(Pedido.id_pedido)).filter(
        func.date(fecha_operacion) == hoy,
        Pedido.estado == 'Completado'
    ).scalar() or 0

    # Serie diaria de ventas (últimos 7 días)
    filas_ventas = db.session.query(
        func.date(fecha_operacion).label('fecha'),
        func.coalesce(func.sum(Pedido.total), 0).label('total')
    ).filter(
        func.date(fecha_operacion) >= inicio_semana,
        Pedido.estado == 'Completado'
    ).group_by(func.date(fecha_operacion)).all()

    mapa_ventas = {str(fila.fecha): float(fila.total or 0) for fila in filas_ventas}

    ventas_diarias_labels = []
    ventas_diarias_data = []
    for i in range(7):
        dia = inicio_semana + timedelta(days=i)
        ventas_diarias_labels.append(dia.strftime('%d/%m'))
        ventas_diarias_data.append(mapa_ventas.get(str(dia), 0))

    top_productos = db.session.query(
        Producto.nombre.label('nombre'),
        func.coalesce(func.sum(DetallePedido.cantidad), 0).label('cantidad'),
        func.coalesce(func.sum(DetallePedido.subtotal), 0).label('monto')
    ).join(DetallePedido, DetallePedido.id_producto == Producto.id_producto).join(
        Pedido, Pedido.id_pedido == DetallePedido.id_pedido
    ).filter(
        Pedido.estado == 'Completado'
    ).group_by(Producto.id_producto, Producto.nombre).order_by(
        func.sum(DetallePedido.cantidad).desc()
    ).limit(5).all()

    top_presentaciones = db.session.query(
        CategoriaPlatillo.nombre.label('nombre'),
        func.coalesce(func.sum(DetallePedido.cantidad), 0).label('cantidad')
    ).join(Producto, Producto.id_categoria_platillo == CategoriaPlatillo.id_categoria_platillo).join(
        DetallePedido, DetallePedido.id_producto == Producto.id_producto
    ).join(
        Pedido, Pedido.id_pedido == DetallePedido.id_pedido
    ).filter(
        Pedido.estado == 'Completado'
    ).group_by(CategoriaPlatillo.id_categoria_platillo, CategoriaPlatillo.nombre).order_by(
        func.sum(DetallePedido.cantidad).desc()
    ).limit(5).all()

    pedidos_recientes = (
        Pedido.query
        .filter(Pedido.estado == 'Completado')
        .order_by(
            Pedido.fecha_entrega.is_(None).asc(),
            Pedido.fecha_entrega.desc(),
            Pedido.fecha.desc(),
        )
        .limit(5)
        .all()
    )

    actividad_reciente = []
    for pedido in pedidos_recientes:
        fecha_ref = pedido.fecha_entrega or pedido.fecha
        actividad_reciente.append({
            'id_pedido': pedido.id_pedido,
            'fecha': fecha_ref,
            'texto': f"Pedido #{pedido.id_pedido} completado",
            'monto': float(pedido.total or 0),
        })

    top_producto = top_productos[0] if top_productos else None
    top_presentacion = top_presentaciones[0] if top_presentaciones else None

    return render_template(
        'dashboard/index.html',
        ventas_hoy_total=float(ventas_hoy_total),
        ventas_diarias_labels=ventas_diarias_labels,
        ventas_diarias_data=ventas_diarias_data,
        top_productos_dashboard=top_productos,
        top_presentaciones_labels=[fila.nombre for fila in top_presentaciones],
        top_presentaciones_data=[int(fila.cantidad or 0) for fila in top_presentaciones],
        top_producto_nombre=top_producto.nombre if top_producto else 'Sin ventas',
        top_producto_cantidad=int(top_producto.cantidad) if top_producto else 0,
        top_presentacion_nombre=top_presentacion.nombre if top_presentacion else 'Sin ventas',
        top_presentacion_cantidad=int(top_presentacion.cantidad) if top_presentacion else 0,
        pedidos_completados_hoy=int(pedidos_completados_hoy),
        actividad_reciente=actividad_reciente,
    )

