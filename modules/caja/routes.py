from . import caja
from flask import render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user
from utils.security import role_required
from models import db, Caja as CajaModel, MovimientoCaja, Proveedor, Pedido, Compra
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

CLOSE_MARKER_DESC = '__CIERRE_CAJA__'


def _obtener_inicio_fin_caja(caja, incluir_momento_actual=False):
    if not caja:
        return None, None

    inicio = caja.fecha
    fin = None

    cierre_marcador = (
        MovimientoCaja.query
        .filter_by(id_caja=caja.id_caja, descripcion=CLOSE_MARKER_DESC)
        .order_by(MovimientoCaja.fecha.desc())
        .first()
    )
    if cierre_marcador:
        fin = cierre_marcador.fecha
    else:
        siguiente_caja = (
            CajaModel.query
            .filter(CajaModel.fecha > caja.fecha)
            .order_by(CajaModel.fecha.asc())
            .first()
        )
        if siguiente_caja:
            fin = siguiente_caja.fecha

    if fin is None:
        if incluir_momento_actual:
            # Permite capturar registros nuevos aunque lleguen con pequeño desfase de zona horaria.
            fin = datetime.now() + timedelta(days=1)
        else:
            # Fallback para cierres históricos sin marcador explícito.
            fin = inicio + timedelta(days=1)

    return inicio, fin


def _query_pedidos_en_periodo(inicio, fin):
    return (
        Pedido.query
        .filter(
            Pedido.estado == 'Completado',
            or_(
                and_(
                    Pedido.fecha_entrega.isnot(None),
                    Pedido.fecha_entrega >= inicio,
                    Pedido.fecha_entrega < fin,
                ),
                and_(
                    Pedido.fecha_entrega.is_(None),
                    Pedido.fecha >= inicio,
                    Pedido.fecha < fin,
                )
            )
        )
    )


def _query_compras_en_periodo(inicio, fin):
    return (
        Compra.query
        .filter(
            Compra.estado == 'Completada',
            Compra.metodo_pago == 'Efectivo',
            or_(
                and_(
                    Compra.fecha_entrega.isnot(None),
                    Compra.fecha_entrega >= inicio,
                    Compra.fecha_entrega < fin,
                ),
                and_(
                    Compra.fecha_entrega.is_(None),
                    Compra.fecha >= inicio,
                    Compra.fecha < fin,
                )
            )
        )
    )


@caja.route('/', methods=['GET'])
@login_required
@role_required(1, 3)
def index():
    caja_abierta = CajaModel.query.filter_by(estado='Abierta').order_by(CajaModel.fecha.desc()).first()

    fecha_param = request.args.get('fecha')
    if caja_abierta:
        fecha_referencia = caja_abierta.fecha.date()
    elif fecha_param:
        try:
            fecha_referencia = datetime.strptime(fecha_param, "%Y-%m-%d").date()
        except ValueError:
            fecha_referencia = datetime.now().date()
    else:
        fecha_referencia = datetime.now().date()

    if caja_abierta:
        inicio_dia, fin_dia = _obtener_inicio_fin_caja(caja_abierta, incluir_momento_actual=True)
    else:
        inicio_dia = datetime.combine(fecha_referencia, datetime.min.time())
        fin_dia = inicio_dia + timedelta(days=1)

    pedidos_dia = _query_pedidos_en_periodo(inicio_dia, fin_dia).order_by(Pedido.fecha.asc()).all()

    ventas_dia = []
    for pedido in pedidos_dia:
        metodo_pago = pedido.meta_pedido.metodo_pago if pedido.meta_pedido else 'Efectivo'
        usuario = (
            pedido.meta_pedido.usuario.username
            if pedido.meta_pedido and pedido.meta_pedido.usuario
            else 'N/D'
        )

        ventas_dia.append({
            'id_pedido': pedido.id_pedido,
            'fecha': pedido.fecha,
            'total': float(pedido.total),
            'metodo_pago': metodo_pago,
            'usuario': usuario,
            'pedido': pedido,
        })

    total_ventas = sum(v['total'] for v in ventas_dia)
    total_efectivo = sum(v['total'] for v in ventas_dia if v['metodo_pago'] == 'Efectivo')
    total_tarjeta = sum(v['total'] for v in ventas_dia if v['metodo_pago'] == 'Tarjeta')
    total_transferencia = sum(v['total'] for v in ventas_dia if v['metodo_pago'] == 'Transferencia')

    compras_egreso_dia = _query_compras_en_periodo(inicio_dia, fin_dia).order_by(Compra.fecha_entrega.desc()).all()
    total_egresos = sum(float(compra.total) for compra in compras_egreso_dia)
    utilidad_diaria = total_ventas - total_egresos

    movimientos_dia = []

    for venta in ventas_dia:
        movimientos_dia.append({
            'fecha': venta['fecha'],
            'tipo': 'Ingreso',
            'referencia': f"Pedido #{venta['id_pedido']}",
            'id_pedido': venta['id_pedido'],
            'id_compra': None,
            'metodo_pago': venta['metodo_pago'],
            'responsable': venta['usuario'],
            'monto': venta['total'],
        })

    for compra in compras_egreso_dia:
        nombre_proveedor = (
            compra.proveedor.persona.nombre
            if compra.proveedor and compra.proveedor.persona
            else 'Proveedor'
        )
        fecha_mov = compra.fecha_entrega or compra.fecha

        movimientos_dia.append({
            'fecha': fecha_mov,
            'tipo': 'Egreso',
            'referencia': f"Compra #{compra.id_compra}",
            'id_pedido': None,
            'id_compra': compra.id_compra,
            'metodo_pago': compra.metodo_pago or 'N/D',
            'responsable': compra.usuario.username if compra.usuario else nombre_proveedor,
            'monto': float(compra.total),
        })

    movimientos_dia.sort(key=lambda item: item['fecha'] or inicio_dia, reverse=True)

    proveedores = (
        Proveedor.query
        .filter_by(estado=True)
        .order_by(Proveedor.id_proveedor.asc())
        .all()
    )

    ultima_caja_cerrada = CajaModel.query.filter_by(estado='Cerrada').order_by(CajaModel.fecha.desc()).first()
    monto_sugerido_apertura = float(ultima_caja_cerrada.monto_final or 0) if ultima_caja_cerrada else 0.0

    cajas = CajaModel.query.order_by(CajaModel.fecha.desc()).limit(10).all()
    return render_template(
        'caja/caja.html',
        cajas=cajas,
        caja_abierta=caja_abierta,
        ultima_caja_cerrada=ultima_caja_cerrada,
        monto_sugerido_apertura=monto_sugerido_apertura,
        fecha_referencia=fecha_referencia,
        ventas_dia=ventas_dia,
        total_ventas=total_ventas,
        total_efectivo=total_efectivo,
        total_tarjeta=total_tarjeta,
        total_transferencia=total_transferencia,
        utilidad_diaria=utilidad_diaria,
        total_egresos=total_egresos,
        movimientos_dia=movimientos_dia,
        compras_egreso_dia=compras_egreso_dia,
        proveedores=proveedores,
    )


def _obtener_o_crear_caja_abierta(id_usuario):
    caja_abierta = CajaModel.query.filter_by(estado='Abierta').order_by(CajaModel.fecha.desc()).first()
    if caja_abierta:
        return caja_abierta

    ultima_caja_cerrada = CajaModel.query.filter_by(estado='Cerrada').order_by(CajaModel.fecha.desc()).first()
    monto_inicial = float(ultima_caja_cerrada.monto_final or 0) if ultima_caja_cerrada else 0.0

    caja_abierta = CajaModel(
        fecha=datetime.now(),
        monto_inicial=monto_inicial,
        estado='Abierta',
        id_usuario=id_usuario,
    )
    from models import db
    db.session.add(caja_abierta)
    db.session.flush()
    return caja_abierta


@caja.route('/abrir', methods=['POST'])
@login_required
@role_required(1, 3)
def abrir_caja():
    try:
        caja_abierta = CajaModel.query.filter_by(estado='Abierta').order_by(CajaModel.fecha.desc()).first()
        if caja_abierta:
            flash(f'Ya existe una caja abierta (#{caja_abierta.id_caja}).', 'warning')
            return redirect(url_for('caja.index'))

        monto_inicial = request.form.get('monto_inicial', type=float)

        if monto_inicial is None:
            ultima_caja_cerrada = CajaModel.query.filter_by(estado='Cerrada').order_by(CajaModel.fecha.desc()).first()
            monto_inicial = float(ultima_caja_cerrada.monto_final or 0) if ultima_caja_cerrada else 0.0

        if monto_inicial < 0:
            flash('El monto inicial no puede ser negativo.', 'warning')
            return redirect(url_for('caja.index'))

        nueva_caja = CajaModel(
            fecha=datetime.now(),
            monto_inicial=float(monto_inicial),
            estado='Abierta',
            id_usuario=current_user.id_usuario,
        )

        db.session.add(nueva_caja)
        db.session.commit()

        flash(
            f'Caja abierta correctamente con monto inicial de ${float(monto_inicial):.2f}.',
            'success'
        )
        return redirect(url_for('caja.index'))

    except Exception as e:
        db.session.rollback()
        flash(str(e), 'danger')
        return redirect(url_for('caja.index'))


@caja.route('/salida-proveedor', methods=['POST'])
@login_required
@role_required(1, 3)
def salida_proveedor():
    from models import db

    try:
        id_proveedor = request.form.get('id_proveedor', type=int)
        monto = request.form.get('monto', type=float)
        descripcion = (request.form.get('descripcion') or '').strip()

        if not id_proveedor:
            flash('Selecciona un proveedor.', 'warning')
            return redirect(url_for('caja.index'))

        if not monto or monto <= 0:
            flash('El monto de salida debe ser mayor a cero.', 'warning')
            return redirect(url_for('caja.index'))

        proveedor = Proveedor.query.get(id_proveedor)
        if not proveedor:
            flash('Proveedor no encontrado.', 'danger')
            return redirect(url_for('caja.index'))

        caja_abierta = _obtener_o_crear_caja_abierta(current_user.id_usuario)

        nombre_proveedor = proveedor.persona.nombre if proveedor.persona else f'Proveedor #{proveedor.id_proveedor}'
        detalle = descripcion if descripcion else f'Pago a proveedor: {nombre_proveedor}'

        movimiento = MovimientoCaja(
            fecha=datetime.now(),
            tipo='Egreso',
            monto=float(monto),
            descripcion=detalle,
            id_caja=caja_abierta.id_caja,
        )
        db.session.add(movimiento)
        db.session.commit()

        flash('Salida de efectivo registrada correctamente.', 'success')
        return redirect(url_for('caja.index'))

    except Exception as e:
        db.session.rollback()
        flash(str(e), 'danger')
        return redirect(url_for('caja.index'))


@caja.route('/cierre', methods=['GET'])
@login_required
@role_required(1, 3)
def cierre():
    caja_abierta = CajaModel.query.filter_by(estado='Abierta').order_by(CajaModel.fecha.desc()).first()

    if not caja_abierta:
        caja_abierta = _obtener_o_crear_caja_abierta(current_user.id_usuario)
        db.session.commit()
        flash('Se abrió una nueva caja automáticamente para poder realizar el cierre.', 'info')

    fecha_referencia = caja_abierta.fecha.date()
    inicio_dia, fin_dia = _obtener_inicio_fin_caja(caja_abierta, incluir_momento_actual=True)

    pedidos_dia = _query_pedidos_en_periodo(inicio_dia, fin_dia).order_by(Pedido.fecha.asc()).all()

    ventas_dia = []
    for pedido in pedidos_dia:
        metodo_pago = pedido.meta_pedido.metodo_pago if pedido.meta_pedido else 'Efectivo'
        usuario = (
            pedido.meta_pedido.usuario.username
            if pedido.meta_pedido and pedido.meta_pedido.usuario
            else 'N/D'
        )
        ventas_dia.append({
            'id_pedido': pedido.id_pedido,
            'fecha': pedido.fecha,
            'total': float(pedido.total),
            'metodo_pago': metodo_pago,
            'usuario': usuario,
        })

    total_ventas = sum(v['total'] for v in ventas_dia)
    total_efectivo = sum(v['total'] for v in ventas_dia if v['metodo_pago'] == 'Efectivo')
    total_tarjeta = sum(v['total'] for v in ventas_dia if v['metodo_pago'] == 'Tarjeta')
    total_transferencia = sum(v['total'] for v in ventas_dia if v['metodo_pago'] == 'Transferencia')

    compras_egreso_dia = _query_compras_en_periodo(inicio_dia, fin_dia).all()
    total_egresos = sum(float(compra.total) for compra in compras_egreso_dia)
    total_neto_efectivo = total_efectivo - total_egresos

    efectivo_sistema = float(caja_abierta.monto_inicial or 0) + total_efectivo - total_egresos

    return render_template(
        'caja/cierre_caja.html',
        caja=caja_abierta,
        hora_actual=datetime.now(),
        fecha_referencia=fecha_referencia,
        total_ventas=total_ventas,
        total_efectivo=total_efectivo,
        total_tarjeta=total_tarjeta,
        total_transferencia=total_transferencia,
        total_egresos=total_egresos,
        total_neto_efectivo=total_neto_efectivo,
        total_movimientos=len(ventas_dia),
        efectivo_sistema=efectivo_sistema,
        compras_egreso_dia=compras_egreso_dia,
    )


@caja.route('/cierre', methods=['POST'])
@login_required
@role_required(1, 3)
def confirmar_cierre():
    try:
        caja_abierta = CajaModel.query.filter_by(estado='Abierta').order_by(CajaModel.fecha.desc()).first()

        if not caja_abierta:
            caja_abierta = _obtener_o_crear_caja_abierta(current_user.id_usuario)
            db.session.flush()

        efectivo_real = request.form.get('efectivo_real', type=float)
        if efectivo_real is None or efectivo_real < 0:
            flash('Ingresa un monto válido para el efectivo contado.', 'warning')
            return redirect(url_for('caja.cierre'))

        inicio_dia, fin_dia = _obtener_inicio_fin_caja(caja_abierta, incluir_momento_actual=True)

        pedidos_efectivo = _query_pedidos_en_periodo(inicio_dia, fin_dia).all()
        total_efectivo = 0.0
        for pedido in pedidos_efectivo:
            metodo_pago = pedido.meta_pedido.metodo_pago if pedido.meta_pedido else 'Efectivo'
            if metodo_pago == 'Efectivo':
                total_efectivo += float(pedido.total)

        compras_egreso = _query_compras_en_periodo(inicio_dia, fin_dia).all()
        total_egresos = sum(float(compra.total) for compra in compras_egreso)

        efectivo_sistema = float(caja_abierta.monto_inicial or 0) + total_efectivo - total_egresos
        diferencia = float(efectivo_real) - efectivo_sistema

        caja_abierta.monto_final = float(efectivo_real)
        caja_abierta.estado = 'Cerrada'

        db.session.add(MovimientoCaja(
            fecha=datetime.now(),
            tipo='Ingreso',
            monto=0,
            descripcion=CLOSE_MARKER_DESC,
            id_caja=caja_abierta.id_caja,
        ))

        db.session.commit()

        flash(
            f'Cierre de caja realizado correctamente. Diferencia de arqueo: ${diferencia:.2f}',
            'success'
        )
        return redirect(url_for('caja.ver_cierre', id_caja=caja_abierta.id_caja))

    except Exception as e:
        db.session.rollback()
        flash(str(e), 'danger')
        return redirect(url_for('caja.cierre'))


@caja.route('/historial', methods=['GET'])
@login_required
@role_required(1, 3)
def historial():
    cierres = CajaModel.query.filter_by(estado='Cerrada').order_by(CajaModel.fecha.desc()).all()
    return render_template('caja/historial_cierre.html', cierres=cierres)


@caja.route('/ver-cierre/<int:id_caja>', methods=['GET'])
@login_required
@role_required(1, 3)
def ver_cierre(id_caja):
    caja_registro = CajaModel.query.get_or_404(id_caja)

    fecha_referencia = caja_registro.fecha.date()
    inicio_dia, fin_dia = _obtener_inicio_fin_caja(caja_registro, incluir_momento_actual=True)

    pedidos_dia = _query_pedidos_en_periodo(inicio_dia, fin_dia).order_by(Pedido.fecha.asc()).all()

    ventas_dia = []
    for pedido in pedidos_dia:
        metodo_pago = pedido.meta_pedido.metodo_pago if pedido.meta_pedido else 'Efectivo'
        cliente_nombre = 'Cliente'
        if pedido.cliente:
            if pedido.cliente.persona:
                nombre = (pedido.cliente.persona.nombre or '').strip()
                apellido_p = (pedido.cliente.persona.apellido_p or '').strip()
                apellido_m = (pedido.cliente.persona.apellido_m or '').strip()
                nombre_completo = ' '.join(part for part in [nombre, apellido_p, apellido_m] if part)
                cliente_nombre = nombre_completo or nombre or 'Cliente'
            elif pedido.cliente.usuario:
                cliente_nombre = pedido.cliente.usuario.username or 'Cliente'

        ventas_dia.append({
            'id_pedido': pedido.id_pedido,
            'fecha': pedido.fecha_entrega or pedido.fecha,
            'total': float(pedido.total),
            'metodo_pago': metodo_pago,
            'cliente': cliente_nombre,
        })

    total_ventas = sum(v['total'] for v in ventas_dia)
    total_efectivo = sum(v['total'] for v in ventas_dia if v['metodo_pago'] == 'Efectivo')
    total_tarjeta = sum(v['total'] for v in ventas_dia if v['metodo_pago'] == 'Tarjeta')
    total_transferencia = sum(v['total'] for v in ventas_dia if v['metodo_pago'] == 'Transferencia')

    compras_egreso_dia = _query_compras_en_periodo(inicio_dia, fin_dia).order_by(Compra.fecha_entrega.asc()).all()
    total_egresos = sum(float(compra.total) for compra in compras_egreso_dia)

    movimientos_corte = []
    for venta in ventas_dia:
        movimientos_corte.append({
            'fecha': venta['fecha'],
            'tipo': 'Ingreso',
            'referencia': f"Pedido #{venta['id_pedido']}",
            'metodo_pago': venta['metodo_pago'],
            'responsable': venta['cliente'],
            'monto': float(venta['total']),
        })

    for compra in compras_egreso_dia:
        nombre_proveedor = (
            compra.proveedor.persona.nombre
            if compra.proveedor and compra.proveedor.persona
            else 'Proveedor'
        )
        fecha_mov = compra.fecha_entrega or compra.fecha

        movimientos_corte.append({
            'fecha': fecha_mov,
            'tipo': 'Egreso',
            'referencia': f"Compra #{compra.id_compra}",
            'metodo_pago': compra.metodo_pago or 'N/D',
            'responsable': compra.usuario.username if compra.usuario else nombre_proveedor,
            'monto': float(compra.total),
        })

    movimientos_corte.sort(key=lambda item: item['fecha'] or inicio_dia)

    efectivo_sistema = float(caja_registro.monto_inicial or 0) + total_efectivo - total_egresos
    efectivo_contado = float(caja_registro.monto_final or 0)
    diferencia = efectivo_contado - efectivo_sistema

    return render_template(
        'caja/ver_cierre.html',
        caja=caja_registro,
        id=id_caja,
        fecha_referencia=fecha_referencia,
        ventas_dia=ventas_dia,
        compras_egreso_dia=compras_egreso_dia,
        total_ventas=total_ventas,
        total_efectivo=total_efectivo,
        total_tarjeta=total_tarjeta,
        total_transferencia=total_transferencia,
        total_egresos=total_egresos,
        movimientos_corte=movimientos_corte,
        efectivo_sistema=efectivo_sistema,
        efectivo_contado=efectivo_contado,
        diferencia=diferencia,
    )


@caja.route('/anular/<int:id_venta>', methods=['GET'])
@login_required
@role_required(1, 3)
def anular_venta(id_venta):
    pedido = Pedido.query.get_or_404(id_venta)
    return render_template('caja/anular_venta.html', venta=pedido, id=id_venta)
