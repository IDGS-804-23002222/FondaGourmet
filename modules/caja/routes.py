import os
from datetime import datetime, timedelta

from flask import current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
try:
    from pymongo import MongoClient
except Exception:
    MongoClient = None
from sqlalchemy import text

from models import Caja as CajaModel
from models import MovimientoCaja, Pedido, db
from mongo_models import guardar_log
from utils.security import role_required
from . import caja

CLOSE_MARKER_DESC = '__CIERRE_CAJA__'
APERTURA_MARKER_DESC = '__APERTURA_CAJA__'
AUTO_HORA_INICIO = 8
AUTO_MINUTO_INICIO = 10
AUTO_HORA_CIERRE = 22
AUTO_MINUTO_CIERRE = 0


def _float(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _inicio_fin_dia(fecha_ref):
    inicio = datetime.combine(fecha_ref, datetime.min.time())
    return inicio, inicio + timedelta(days=1)


def _ya_hubo_apertura_hoy(fecha_ref):
    inicio, fin = _inicio_fin_dia(fecha_ref)
    return (
        CajaModel.query
        .filter(CajaModel.fecha >= inicio, CajaModel.fecha < fin)
        .count() > 0
    )


def _ya_hubo_cierre_hoy(fecha_ref):
    inicio, fin = _inicio_fin_dia(fecha_ref)
    return (
        MovimientoCaja.query
        .filter(
            MovimientoCaja.descripcion == CLOSE_MARKER_DESC,
            MovimientoCaja.fecha >= inicio,
            MovimientoCaja.fecha < fin,
        )
        .count() > 0
    )


def _obtener_caja_abierta():
    return CajaModel.query.filter_by(estado='Abierta').order_by(CajaModel.fecha.desc()).first()


def _obtener_rango_caja(caja_sesion, incluir_ahora=False):
    if not caja_sesion:
        return None, None

    inicio = caja_sesion.fecha
    cierre = (
        MovimientoCaja.query
        .filter_by(id_caja=caja_sesion.id_caja, descripcion=CLOSE_MARKER_DESC)
        .order_by(MovimientoCaja.fecha.desc())
        .first()
    )

    if cierre:
        return inicio, cierre.fecha

    if incluir_ahora:
        return inicio, datetime.now() + timedelta(seconds=5)

    return inicio, inicio + timedelta(days=1)


def _resumen_pedidos_pagados_sql(inicio, fin):
    sql = text(
        """
        SELECT
            COALESCE(SUM(p.total), 0) AS total_ventas,
            COALESCE(SUM(CASE WHEN COALESCE(pm.metodo_pago, 'Efectivo') = 'Efectivo' THEN p.total ELSE 0 END), 0) AS total_efectivo,
            COALESCE(SUM(CASE WHEN COALESCE(pm.metodo_pago, '') = 'Tarjeta' THEN p.total ELSE 0 END), 0) AS total_tarjeta,
            COALESCE(SUM(CASE WHEN COALESCE(pm.metodo_pago, '') = 'Transferencia' THEN p.total ELSE 0 END), 0) AS total_transferencia,
            COUNT(*) AS total_pedidos_pagados
        FROM pedidos p
        LEFT JOIN pedidos_meta pm ON pm.id_pedido = p.id_pedido
        WHERE p.estado_pago = 'Pagado'
          AND COALESCE(p.fecha_entrega, p.fecha) >= :inicio
          AND COALESCE(p.fecha_entrega, p.fecha) < :fin
        """
    )
    row = db.session.execute(sql, {'inicio': inicio, 'fin': fin}).mappings().first()

    sql_cancelado = text(
        """
        SELECT COALESCE(SUM(p.total), 0) AS total_cancelado
        FROM pedidos p
        WHERE (p.estado = 'Cancelado' OR p.estado_pago = 'Cancelado')
          AND COALESCE(p.fecha_entrega, p.fecha) >= :inicio
          AND COALESCE(p.fecha_entrega, p.fecha) < :fin
        """
    )
    row_cancelado = db.session.execute(sql_cancelado, {'inicio': inicio, 'fin': fin}).mappings().first()

    return {
        'total_ventas': _float(row['total_ventas'] if row else 0),
        'total_efectivo': _float(row['total_efectivo'] if row else 0),
        'total_tarjeta': _float(row['total_tarjeta'] if row else 0),
        'total_transferencia': _float(row['total_transferencia'] if row else 0),
        'total_pedidos_pagados': int((row['total_pedidos_pagados'] if row else 0) or 0),
        'total_cancelado': _float(row_cancelado['total_cancelado'] if row_cancelado else 0),
    }


def _obtener_pedidos_pagados_periodo(inicio, fin):
    return (
        Pedido.query
        .filter(
            Pedido.estado_pago == 'Pagado',
            db.func.coalesce(Pedido.fecha_entrega, Pedido.fecha) >= inicio,
            db.func.coalesce(Pedido.fecha_entrega, Pedido.fecha) < fin,
        )
        .order_by(Pedido.fecha.desc())
        .all()
    )


def _obtener_pedidos_anulables_periodo(inicio, fin):
    return (
        Pedido.query
        .filter(
            Pedido.estado_pago == 'Pagado',
            Pedido.estado != 'Cancelado',
            db.func.coalesce(Pedido.fecha_entrega, Pedido.fecha) >= inicio,
            db.func.coalesce(Pedido.fecha_entrega, Pedido.fecha) < fin,
        )
        .order_by(Pedido.fecha.desc())
        .all()
    )


def _obtener_total_egresos(caja_sesion):
    if not caja_sesion:
        return 0.0

    total = (
        db.session.query(db.func.sum(MovimientoCaja.monto))
        .filter(
            MovimientoCaja.id_caja == caja_sesion.id_caja,
            MovimientoCaja.tipo == 'Egreso',
        )
        .scalar()
    )
    return _float(total)


def _obtener_usuario_autocaja():
    if getattr(current_user, 'is_authenticated', False) and getattr(current_user, 'id_rol', None) in (1, 3):
        return current_user

    ultimo = CajaModel.query.order_by(CajaModel.fecha.desc()).first()
    if ultimo and ultimo.usuario and ultimo.usuario.id_rol in (1, 3):
        return ultimo.usuario

    from models import Usuario

    return Usuario.query.filter(Usuario.id_rol.in_([1, 3])).order_by(Usuario.id_usuario.asc()).first()


def _guardar_snapshot_mongo(caja_sesion, resumen, total_egresos, id_usuario_cierre):
    mongo_db = getattr(current_app, 'mongo', None)

    if mongo_db is None:
        if MongoClient is None:
            current_app.logger.warning('Mongo snapshot omitido: pymongo no instalado')
            return False
        uri = current_app.config.get('MONGO_URI') or os.getenv('MONGO_URI') or 'mongodb://localhost:27017/fondaGourmet'
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=2500)
            default_db = client.get_default_database()
            mongo_db = default_db if default_db is not None else client.get_database('fondaGourmet')
            client.admin.command('ping')
        except Exception as exc:
            current_app.logger.warning(f'Mongo snapshot omitido (sin conexion): {exc}')
            return False

    try:
        mongo_db.caja_snapshots.insert_one({
            'fecha': datetime.utcnow(),
            'id_caja': caja_sesion.id_caja,
            'apertura': caja_sesion.fecha,
            'cierre': datetime.utcnow(),
            'monto_inicial': _float(caja_sesion.monto_inicial),
            'monto_final': _float(caja_sesion.monto_final),
            'total_ventas': _float(resumen['total_ventas']),
            'total_cancelado': _float(resumen['total_cancelado']),
            'total_efectivo': _float(resumen['total_efectivo']),
            'total_tarjeta': _float(resumen['total_tarjeta']),
            'total_transferencia': _float(resumen['total_transferencia']),
            'total_egresos': _float(total_egresos),
            'usuario_cierre': id_usuario_cierre,
        })
        return True
    except Exception as exc:
        current_app.logger.warning(f'No se pudo crear snapshot de caja: {exc}')
        return False


def _crear_caja_apertura(id_usuario, monto_inicial, fecha_apertura=None, motivo='manual'):
    fecha_apertura = fecha_apertura or datetime.now()
    sesion = CajaModel(
        fecha=fecha_apertura,
        monto_inicial=max(0.0, _float(monto_inicial)),
        estado='Abierta',
        id_usuario=id_usuario,
    )
    db.session.add(sesion)
    db.session.flush()

    db.session.add(MovimientoCaja(
        fecha=fecha_apertura,
        tipo='Ingreso',
        monto=0,
        descripcion=f'{APERTURA_MARKER_DESC}:{motivo}',
        id_caja=sesion.id_caja,
    ))

    return sesion


def _cerrar_caja(caja_sesion, efectivo_real, id_usuario_cierre, fecha_cierre=None, motivo='manual'):
    if not caja_sesion:
        return False, 'No hay caja abierta para cerrar', None

    if (caja_sesion.estado or '').strip().lower() != 'abierta':
        return False, 'La caja ya esta cerrada', None

    fecha_cierre = fecha_cierre or datetime.now()

    inicio, fin = _obtener_rango_caja(caja_sesion, incluir_ahora=True)
    resumen = _resumen_pedidos_pagados_sql(inicio, fin)
    total_egresos = _obtener_total_egresos(caja_sesion)

    efectivo_sistema = _float(caja_sesion.monto_inicial) + _float(resumen['total_efectivo']) - total_egresos
    diferencia = _float(efectivo_real) - efectivo_sistema

    caja_sesion.monto_final = _float(efectivo_real)
    caja_sesion.estado = 'Cerrada'

    db.session.add(MovimientoCaja(
        fecha=fecha_cierre,
        tipo='Ingreso',
        monto=0,
        descripcion=f'{CLOSE_MARKER_DESC}:{motivo}',
        id_caja=caja_sesion.id_caja,
    ))

    guardar_log(
        current_app,
        action='cierre_caja',
        descripcion=f'Cierre de caja #{caja_sesion.id_caja} ({motivo}) diferencia={diferencia:.2f}',
        id_usuario=id_usuario_cierre,
        ip=request.remote_addr if request else None,
    )

    _guardar_snapshot_mongo(caja_sesion, resumen, total_egresos, id_usuario_cierre)

    return True, 'Caja cerrada correctamente', {
        'resumen': resumen,
        'total_egresos': total_egresos,
        'efectivo_sistema': efectivo_sistema,
        'diferencia': diferencia,
    }


def ejecutar_automatizacion_caja():
    """Autocierre/apertura inspirado en Buffet, adaptado para Fonda.
    Llamar desde app.before_request.
    """
    try:
        ahora = datetime.now()
        today = ahora.date()

        caja_abierta = _obtener_caja_abierta()

        hora_cierre = ahora.replace(hour=AUTO_HORA_CIERRE, minute=AUTO_MINUTO_CIERRE, second=0, microsecond=0)
        if caja_abierta and ahora >= hora_cierre and not _ya_hubo_cierre_hoy(today):
            inicio, fin = _obtener_rango_caja(caja_abierta, incluir_ahora=True)
            resumen = _resumen_pedidos_pagados_sql(inicio, fin)
            total_egresos = _obtener_total_egresos(caja_abierta)
            efectivo_sistema = _float(caja_abierta.monto_inicial) + _float(resumen['total_efectivo']) - total_egresos
            id_usuario = caja_abierta.id_usuario

            ok, _, _ = _cerrar_caja(
                caja_abierta,
                efectivo_real=max(0.0, efectivo_sistema),
                id_usuario_cierre=id_usuario,
                fecha_cierre=hora_cierre,
                motivo='auto',
            )
            if ok:
                db.session.commit()
                caja_abierta = None

        hora_apertura = ahora.replace(hour=AUTO_HORA_INICIO, minute=AUTO_MINUTO_INICIO, second=0, microsecond=0)
        if ahora >= hora_apertura and not _ya_hubo_apertura_hoy(today):
            if not caja_abierta:
                usuario = _obtener_usuario_autocaja()
                if usuario:
                    ultima_cerrada = CajaModel.query.filter_by(estado='Cerrada').order_by(CajaModel.fecha.desc()).first()
                    monto_inicial = _float(ultima_cerrada.monto_final if ultima_cerrada else 0)
                    _crear_caja_apertura(usuario.id_usuario, monto_inicial, fecha_apertura=hora_apertura, motivo='auto')

                    guardar_log(
                        current_app,
                        action='apertura_caja',
                        descripcion='Apertura automatica de caja',
                        id_usuario=usuario.id_usuario,
                        ip=request.remote_addr if request else None,
                    )
                    db.session.commit()

    except Exception as exc:
        db.session.rollback()
        current_app.logger.warning(f'Automatizacion de caja omitida: {exc}')


@caja.route('/', methods=['GET'])
@login_required
@role_required(1, 3)
def index():
    caja_abierta = _obtener_caja_abierta()

    fecha_referencia = datetime.now().date()
    if caja_abierta:
        inicio, fin = _obtener_rango_caja(caja_abierta, incluir_ahora=True)
    else:
        inicio, fin = _inicio_fin_dia(fecha_referencia)

    resumen = _resumen_pedidos_pagados_sql(inicio, fin)
    pedidos_pagados = _obtener_pedidos_pagados_periodo(inicio, fin)
    anulables = _obtener_pedidos_anulables_periodo(inicio, fin)
    total_egresos = _obtener_total_egresos(caja_abierta)

    monto_inicial = _float(caja_abierta.monto_inicial if caja_abierta else 0)
    dinero_en_caja = monto_inicial + _float(resumen['total_efectivo']) - total_egresos

    ultima_caja_cerrada = CajaModel.query.filter_by(estado='Cerrada').order_by(CajaModel.fecha.desc()).first()
    monto_sugerido_apertura = _float(ultima_caja_cerrada.monto_final if ultima_caja_cerrada else 0)

    return render_template(
        'caja/dashboard.html',
        caja_abierta=caja_abierta,
        resumen=resumen,
        pedidos_pagados=pedidos_pagados,
        pedidos_anulables=anulables,
        dinero_en_caja=dinero_en_caja,
        total_egresos=total_egresos,
        monto_sugerido_apertura=monto_sugerido_apertura,
        fecha_apertura=caja_abierta.fecha if caja_abierta else None,
    )


@caja.route('/api/stats', methods=['GET'])
@login_required
@role_required(1, 3)
def api_stats():
    caja_abierta = _obtener_caja_abierta()
    if caja_abierta:
        inicio, fin = _obtener_rango_caja(caja_abierta, incluir_ahora=True)
    else:
        inicio, fin = _inicio_fin_dia(datetime.now().date())

    resumen = _resumen_pedidos_pagados_sql(inicio, fin)
    total_egresos = _obtener_total_egresos(caja_abierta)
    monto_inicial = _float(caja_abierta.monto_inicial if caja_abierta else 0)

    return jsonify({
        'success': True,
        'caja_abierta': bool(caja_abierta),
        'dinero_en_caja': monto_inicial + _float(resumen['total_efectivo']) - total_egresos,
        'resumen': resumen,
        'total_egresos': total_egresos,
    })


@caja.route('/abrir', methods=['POST'])
@login_required
@role_required(1, 3)
def abrir_caja():
    try:
        if _obtener_caja_abierta():
            flash('Ya existe una caja abierta.', 'warning')
            return redirect(url_for('caja.index'))

        if _ya_hubo_apertura_hoy(datetime.now().date()):
            flash('La caja solo puede abrirse una vez por dia.', 'warning')
            return redirect(url_for('caja.index'))

        monto_inicial = request.form.get('monto_inicial', type=float)
        if monto_inicial is None or monto_inicial < 0:
            flash('Ingresa un monto inicial valido.', 'warning')
            return redirect(url_for('caja.index'))

        _crear_caja_apertura(current_user.id_usuario, monto_inicial, motivo='manual')

        guardar_log(
            current_app,
            action='apertura_caja',
            descripcion=f'Apertura manual de caja por usuario #{current_user.id_usuario}',
            id_usuario=current_user.id_usuario,
            ip=request.remote_addr,
        )

        db.session.commit()
        flash('Caja abierta correctamente.', 'success')
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error(f'Error abriendo caja: {exc}')
        flash('No se pudo abrir la caja.', 'danger')

    return redirect(url_for('caja.index'))


@caja.route('/cierre', methods=['GET'])
@login_required
@role_required(1, 3)
def cierre():
    caja_abierta = _obtener_caja_abierta()
    if not caja_abierta:
        flash('No hay caja abierta para cerrar.', 'warning')
        return redirect(url_for('caja.index'))

    inicio, fin = _obtener_rango_caja(caja_abierta, incluir_ahora=True)
    resumen = _resumen_pedidos_pagados_sql(inicio, fin)
    total_egresos = _obtener_total_egresos(caja_abierta)
    efectivo_sistema = _float(caja_abierta.monto_inicial) + _float(resumen['total_efectivo']) - total_egresos

    return render_template(
        'caja/cierre_caja.html',
        caja=caja_abierta,
        fecha_referencia=datetime.now().date(),
        total_ventas=resumen['total_ventas'],
        total_efectivo=resumen['total_efectivo'],
        total_tarjeta=resumen['total_tarjeta'],
        total_transferencia=resumen['total_transferencia'],
        total_egresos=total_egresos,
        total_neto_efectivo=resumen['total_efectivo'] - total_egresos,
        total_movimientos=resumen['total_pedidos_pagados'],
        efectivo_sistema=efectivo_sistema,
        compras_egreso_dia=[],
    )


@caja.route('/cierre', methods=['POST'])
@login_required
@role_required(1, 3)
def confirmar_cierre():
    try:
        caja_abierta = _obtener_caja_abierta()
        if not caja_abierta:
            flash('No hay caja abierta para cerrar.', 'warning')
            return redirect(url_for('caja.index'))

        if _ya_hubo_cierre_hoy(datetime.now().date()):
            flash('La caja solo puede cerrarse una vez por dia.', 'warning')
            return redirect(url_for('caja.index'))

        efectivo_real = request.form.get('efectivo_real', type=float)
        if efectivo_real is None or efectivo_real < 0:
            flash('Ingresa un monto valido para cierre.', 'warning')
            return redirect(url_for('caja.cierre'))

        ok, msg, payload = _cerrar_caja(
            caja_abierta,
            efectivo_real=efectivo_real,
            id_usuario_cierre=current_user.id_usuario,
            motivo='manual',
        )
        if not ok:
            flash(msg, 'danger')
            return redirect(url_for('caja.cierre'))

        db.session.commit()
        flash(f"{msg}. Diferencia: ${payload['diferencia']:.2f}", 'success')
        return redirect(url_for('caja.ver_cierre', id_caja=caja_abierta.id_caja))

    except Exception as exc:
        db.session.rollback()
        current_app.logger.error(f'Error en cierre de caja: {exc}')
        flash('No se pudo cerrar la caja.', 'danger')
        return redirect(url_for('caja.cierre'))


@caja.route('/historial', methods=['GET'])
@login_required
@role_required(1, 3)
def historial():
    cierres = CajaModel.query.filter_by(estado='Cerrada').order_by(CajaModel.fecha.desc()).all()

    cierres_detalle = []
    for cierre in cierres:
        inicio, fin = _obtener_rango_caja(cierre, incluir_ahora=False)
        resumen = _resumen_pedidos_pagados_sql(inicio, fin)
        total_egresos = _obtener_total_egresos(cierre)
        efectivo_sistema = _float(cierre.monto_inicial) + _float(resumen['total_efectivo']) - total_egresos

        cierres_detalle.append({
            'caja': cierre,
            'resumen': resumen,
            'total_egresos': total_egresos,
            'efectivo_sistema': efectivo_sistema,
            'diferencia': _float(cierre.monto_final) - efectivo_sistema,
        })

    return render_template('caja/historial_cierre.html', cierres_detalle=cierres_detalle, cierres=cierres)


@caja.route('/ver-cierre/<int:id_caja>', methods=['GET'])
@login_required
@role_required(1, 3)
def ver_cierre(id_caja):
    caja_registro = CajaModel.query.get_or_404(id_caja)
    inicio, fin = _obtener_rango_caja(caja_registro, incluir_ahora=False)

    resumen = _resumen_pedidos_pagados_sql(inicio, fin)
    pedidos_pagados = _obtener_pedidos_pagados_periodo(inicio, fin)

    ventas_dia = []
    for pedido in pedidos_pagados:
        cliente_nombre = 'Cliente'
        if pedido.cliente and pedido.cliente.persona:
            partes = [
                (pedido.cliente.persona.nombre or '').strip(),
                (pedido.cliente.persona.apellido_p or '').strip(),
                (pedido.cliente.persona.apellido_m or '').strip(),
            ]
            cliente_nombre = ' '.join([p for p in partes if p]).strip() or 'Cliente'
        elif pedido.cliente and pedido.cliente.usuario:
            cliente_nombre = pedido.cliente.usuario.username or 'Cliente'

        ventas_dia.append({
            'id_pedido': pedido.id_pedido,
            'fecha': pedido.fecha_entrega or pedido.fecha,
            'cliente': cliente_nombre,
            'metodo_pago': pedido.meta_pedido.metodo_pago if pedido.meta_pedido else 'Efectivo',
            'total': _float(pedido.total),
        })

    total_egresos = _obtener_total_egresos(caja_registro)

    egresos = (
        MovimientoCaja.query
        .filter(
            MovimientoCaja.id_caja == caja_registro.id_caja,
            MovimientoCaja.tipo == 'Egreso',
        )
        .order_by(MovimientoCaja.fecha.asc())
        .all()
    )

    compras_egreso_dia = []
    movimientos_corte = []
    for venta in ventas_dia:
        movimientos_corte.append({
            'fecha': venta['fecha'],
            'tipo': 'Ingreso',
            'referencia': f"Pedido #{venta['id_pedido']}",
            'metodo_pago': venta['metodo_pago'],
            'responsable': venta['cliente'],
            'monto': _float(venta['total']),
        })

    for egreso in egresos:
        compras_egreso_dia.append({
            'id_compra': None,
            'fecha': egreso.fecha,
            'fecha_entrega': egreso.fecha,
            'total': _float(egreso.monto),
            'metodo_pago': 'Efectivo',
            'descripcion': egreso.descripcion,
        })
        movimientos_corte.append({
            'fecha': egreso.fecha,
            'tipo': 'Egreso',
            'referencia': egreso.descripcion or 'Egreso de caja',
            'metodo_pago': 'Efectivo',
            'responsable': caja_registro.usuario.username if caja_registro.usuario else 'N/D',
            'monto': _float(egreso.monto),
        })

    movimientos_corte.sort(key=lambda item: item['fecha'] or inicio)

    efectivo_sistema = _float(caja_registro.monto_inicial) + _float(resumen['total_efectivo']) - total_egresos
    efectivo_contado = _float(caja_registro.monto_final)

    return render_template(
        'caja/ver_cierre.html',
        caja=caja_registro,
        id=id_caja,
        fecha_referencia=caja_registro.fecha.date(),
        ventas_dia=ventas_dia,
        compras_egreso_dia=compras_egreso_dia,
        total_ventas=resumen['total_ventas'],
        total_efectivo=resumen['total_efectivo'],
        total_tarjeta=resumen['total_tarjeta'],
        total_transferencia=resumen['total_transferencia'],
        total_egresos=total_egresos,
        movimientos_corte=movimientos_corte,
        efectivo_sistema=efectivo_sistema,
        efectivo_contado=efectivo_contado,
        diferencia=efectivo_contado - efectivo_sistema,
    )


@caja.route('/anular/<int:id_venta>', methods=['GET'])
@login_required
@role_required(1, 3)
def anular_venta(id_venta):
    pedido = Pedido.query.get_or_404(id_venta)
    return render_template('caja/anular_venta.html', venta=pedido, id=id_venta)


@caja.route('/anular/<int:id_venta>', methods=['POST'])
@login_required
@role_required(1, 3)
def confirmar_anular_venta(id_venta):
    try:
        caja_abierta = _obtener_caja_abierta()
        if not caja_abierta:
            return jsonify({'success': False, 'message': 'No hay caja abierta para registrar la anulacion'}), 400

        pedido = Pedido.query.get(id_venta)
        if not pedido:
            return jsonify({'success': False, 'message': 'Pedido no encontrado'}), 404

        if (pedido.estado or '').strip().lower() == 'cancelado' or (pedido.estado_pago or '').strip().lower() == 'cancelado':
            return jsonify({'success': False, 'message': 'El pedido ya estaba cancelado'}), 409

        metodo_pago = (pedido.meta_pedido.metodo_pago if pedido.meta_pedido else 'Efectivo') or 'Efectivo'
        if (pedido.estado_pago or '').strip().lower() != 'pagado':
            return jsonify({'success': False, 'message': 'Solo se pueden anular ventas pagadas'}), 409

        if metodo_pago == 'Efectivo':
            db.session.add(MovimientoCaja(
                fecha=datetime.now(),
                tipo='Egreso',
                monto=_float(pedido.total),
                descripcion=f'Anulacion de venta Pedido #{pedido.id_pedido}',
                id_caja=caja_abierta.id_caja,
            ))

        pedido.estado = 'Cancelado'
        pedido.estado_pago = 'Cancelado'

        if pedido.meta_pedido:
            pedido.meta_pedido.id_usuario = current_user.id_usuario

        guardar_log(
            current_app,
            action='anulacion_venta',
            descripcion=f'Pedido #{pedido.id_pedido} anulado por usuario #{current_user.id_usuario}',
            id_usuario=current_user.id_usuario,
            ip=request.remote_addr,
        )

        db.session.commit()
        return jsonify({'success': True, 'message': 'Venta anulada correctamente'})

    except Exception as exc:
        db.session.rollback()
        current_app.logger.error(f'Error anulando venta: {exc}')
        return jsonify({'success': False, 'message': 'No se pudo anular la venta'}), 500
