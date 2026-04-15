from . import compras
from flask import render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_required, current_user
from utils.security import role_required
from models import db, Compra, DetalleCompra, MateriaPrima, Proveedor
from .services import (
    obtener_compras, obtener_compra, completar_compra,
    aplicar_cambios_compra, crear_solicitud_compra_manual,
    obtener_materias_faltantes_produccion, obtener_materias_alerta_stock_bajo,
    recibir_detalle_compra, eliminar_solicitud_compra,
    obtener_efectivo_disponible_para_compra, _asegurar_esquema_compras,
)
from datetime import datetime
import re


def _obtener_proveedores_relacionados_compra(compra):
    ids = {
        detalle.materia_prima.id_proveedor
        for detalle in compra.detalles
        if detalle.materia_prima and detalle.materia_prima.id_proveedor
    }
    if not ids:
        return []

    return Proveedor.query.filter(Proveedor.id_proveedor.in_(ids)).order_by(Proveedor.id_proveedor.asc()).all()


def _aplicar_datos_generales_compra(compra, form, usar_hora_actual=False):
    fecha_entrega = form.get('fecha_entrega')
    metodo_pago = form.get('metodo_pago')
    id_proveedor = form.get('id_proveedor', type=int)

    if fecha_entrega:
        fecha_base = datetime.strptime(fecha_entrega, "%Y-%m-%d")
        if usar_hora_actual:
            ahora = datetime.now()
            compra.fecha_entrega = datetime(
                fecha_base.year,
                fecha_base.month,
                fecha_base.day,
                ahora.hour,
                ahora.minute,
                ahora.second,
            )
        else:
            compra.fecha_entrega = fecha_base

    if metodo_pago:
        compra.metodo_pago = metodo_pago

    tipo_pago = form.get('tipo_pago')
    if tipo_pago in {'Contado', 'Credito'}:
        compra.tipo_pago = tipo_pago

    if id_proveedor:
        proveedores_permitidos = {p.id_proveedor for p in _obtener_proveedores_relacionados_compra(compra)}
        if proveedores_permitidos and id_proveedor not in proveedores_permitidos:
            raise ValueError("El proveedor no está relacionado con las materias primas de esta compra")
        compra.id_proveedor = id_proveedor


def _validar_datos_tarjeta_compra(numero, titular, vencimiento, cvv):
    numero_limpio = re.sub(r'\s+', '', (numero or '').strip())
    titular = (titular or '').strip()
    vencimiento = (vencimiento or '').strip()
    cvv = (cvv or '').strip()

    if not re.fullmatch(r'\d{13,19}', numero_limpio):
        return False, "Numero de tarjeta invalido", None

    if len(titular) < 3:
        return False, "Ingresa el nombre del titular", None

    if not re.fullmatch(r'(0[1-9]|1[0-2])/\d{2}', vencimiento):
        return False, "Fecha de vencimiento invalida (MM/AA)", None

    if not re.fullmatch(r'\d{3,4}', cvv):
        return False, "CVV invalido", None

    return True, None, numero_limpio[-4:]


def _validar_requisitos_recepcion(compra):
    if not compra.id_proveedor:
        return False, "Selecciona un proveedor antes de recibir la compra"
    if not compra.metodo_pago:
        return False, "Selecciona un metodo de pago antes de recibir la compra"
    if not compra.fecha_entrega:
        return False, "Selecciona la fecha de entrega antes de recibir la compra"
    if compra.metodo_pago == 'Tarjeta' and (not compra.tarjeta_titular or not compra.tarjeta_ultimos4 or not compra.tarjeta_vencimiento):
        return False, "Guarda los datos de tarjeta antes de recibir la compra"
    return True, None


def _registrar_log_entrada_almacen(compra, id_usuario_receptor):
    try:
        mongo_db = getattr(current_app, 'mongo', None)
        if mongo_db is None:
            return

        detalles = []
        for det in compra.detalles:
            detalles.append({
                'id_detalle': det.id_detalle,
                'id_materia': det.id_materia,
                'materia': det.materia_prima.nombre if det.materia_prima else 'Materia Prima',
                'cantidad': float(det.cantidad or 0),
                'precio_u': float(det.precio_u or 0),
                'subtotal': float(det.subtotal or 0),
                'recibido': bool(getattr(det, 'recibido', False)),
            })

        mongo_db.entradas_almacen.insert_one({
            'fecha': datetime.utcnow(),
            'tipo_evento': 'Entrada de Almacen',
            'id_compra': compra.id_compra,
            'id_proveedor': compra.id_proveedor,
            'proveedor': compra.proveedor.persona.nombre if compra.proveedor and compra.proveedor.persona else None,
            'metodo_pago': compra.metodo_pago,
            'tipo_pago': compra.tipo_pago,
            'estado_compra': compra.estado,
            'total': float(compra.total or 0),
            'id_usuario_receptor': id_usuario_receptor,
            'usuario_receptor': getattr(current_user, 'username', None),
            'detalles': detalles,
        })
    except Exception as exc:
        current_app.logger.warning(f'No se pudo registrar Entrada de Almacen en Mongo: {exc}')


@compras.route('/guardar_pago/<int:id>', methods=['POST'])
@login_required
@role_required(1, 3)
def guardar_pago(id):
    try:
        _asegurar_esquema_compras()
        compra = Compra.query.get(id)

        if not compra:
            flash("Compra no encontrada", "danger")
            return redirect(url_for('compras.index'))

        metodo_pago = (request.form.get('metodo_pago') or '').strip().title()
        if metodo_pago not in {'Efectivo', 'Tarjeta', 'Transferencia'}:
            flash('Metodo de pago invalido', 'danger')
            return redirect(url_for('compras.ver', id=id))

        tipo_pago = (request.form.get('tipo_pago') or 'Contado').strip().title()
        if tipo_pago not in {'Contado', 'Credito'}:
            flash('Tipo de pago invalido (Contado/Credito)', 'danger')
            return redirect(url_for('compras.ver', id=id))

        compra.metodo_pago = metodo_pago
        compra.tipo_pago = tipo_pago

        if metodo_pago == 'Tarjeta':
            ok, error, ultimos4 = _validar_datos_tarjeta_compra(
                request.form.get('numero_tarjeta'),
                request.form.get('tarjeta_titular'),
                request.form.get('tarjeta_vencimiento'),
                request.form.get('tarjeta_cvv'),
            )
            if not ok:
                db.session.rollback()
                flash(error, 'warning')
                return redirect(url_for('compras.ver', id=id))

            compra.tarjeta_titular = (request.form.get('tarjeta_titular') or '').strip()
            compra.tarjeta_ultimos4 = ultimos4
            compra.tarjeta_vencimiento = (request.form.get('tarjeta_vencimiento') or '').strip()
        else:
            compra.tarjeta_titular = None
            compra.tarjeta_ultimos4 = None
            compra.tarjeta_vencimiento = None

        db.session.commit()
        flash('Pago guardado correctamente', 'success')
        return redirect(url_for('compras.ver', id=id))

    except Exception as e:
        db.session.rollback()
        flash(str(e), 'danger')
        return redirect(url_for('compras.ver', id=id))

@compras.route('/')
@login_required
@role_required(1, 3)
def index():
    _asegurar_esquema_compras()
    compras, error = obtener_compras()
    if error:
        current_app.logger.error(f"Error al cargar compras: {error}")
        flash("Error al cargar las compras", "danger")
        return redirect(url_for('pedidos.index'))

    hoy = datetime.now().date()
    compras_completadas_hoy = sum(
        1
        for compra in compras
        if compra['estado'] in ['Completada', 'Completado']
        and compra['fecha_entrega']
        and compra['fecha_entrega'].date() == hoy
    )
    compras_solicitadas = sum(1 for compra in compras if compra['estado'] == 'Solicitada')

    return render_template(
        'compras/registro_compra.html',
        compras=compras,
        compras_completadas_hoy=compras_completadas_hoy,
        compras_solicitadas=compras_solicitadas,
        proveedores=Proveedor.query.filter_by(estado=True).order_by(Proveedor.id_proveedor.asc()).all(),
    )

@compras.route('/crear', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def crear():
    _asegurar_esquema_compras()
    if current_user.id_rol == 2 and not session.get('compra_alerta_autorizada'):
        flash('Como cocinero solo puedes crear solicitudes de compra desde alertas.', 'warning')
        return redirect(url_for('produccion.index'))

    alerta_stock = request.args.get('alerta_stock', type=int)

    if request.method == 'POST':
        resultado, mensaje = crear_solicitud_compra_manual(request.form, current_user.id_usuario)

        if resultado:
            flash(mensaje, 'success')
            session.pop('compra_alerta_autorizada', None)

            if current_user.id_rol == 2:
                return redirect(url_for('produccion.index'))

            if isinstance(resultado, list):
                return redirect(url_for('compras.index'))
            return redirect(url_for('compras.ver', id=resultado))

        flash(mensaje, 'danger')
        return redirect(url_for('compras.crear'))

    id_materia_alerta = request.args.get('id_materia', type=int)

    materias = MateriaPrima.query.filter_by(estado=True).order_by(MateriaPrima.nombre.asc()).all()
    proveedores = Proveedor.query.filter_by(estado=True).order_by(Proveedor.id_proveedor.asc()).all()
    ids_materias = [m.id_materia for m in materias]
    materias_solicitadas = set()

    if ids_materias:
        filas_solicitadas = (
            db.session.query(DetalleCompra.id_materia)
            .join(Compra, Compra.id_compra == DetalleCompra.id_compra)
            .filter(
                Compra.estado.in_(['Solicitada', 'En Camino']),
                DetalleCompra.id_materia.in_(ids_materias)
            )
            .distinct()
            .all()
        )
        materias_solicitadas = {fila[0] for fila in filas_solicitadas}

    if alerta_stock:
        sugerencias = obtener_materias_alerta_stock_bajo(id_materia_alerta)
    elif id_materia_alerta:
        sugerencias = obtener_materias_alerta_stock_bajo(id_materia_alerta)
    else:
        sugerencias = obtener_materias_faltantes_produccion(id_materia_alerta)

    return render_template(
        'compras/crear.html',
        materias=materias,
        proveedores=proveedores,
        materias_solicitadas=materias_solicitadas,
        sugerencias=sugerencias,
        id_materia_alerta=id_materia_alerta,
        alerta_stock=bool(alerta_stock),
    )

@compras.route('/ver/<int:id>')
@login_required
@role_required(1, 3)
def ver(id):
    _asegurar_esquema_compras()
    compra, error = obtener_compra(id)

    if not compra:
        flash("Compra no encontrada", "danger")
        return redirect(url_for('compras.index'))

    proveedores = _obtener_proveedores_relacionados_compra(Compra.query.get(id))
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')

    efectivo_disponible, caja_abierta = obtener_efectivo_disponible_para_compra()

    return render_template(
        'compras/ver.html',
        compra=compra,
        proveedores=proveedores,
        fecha_hoy=fecha_hoy,
        efectivo_disponible=efectivo_disponible,
        caja_abierta=caja_abierta,
    )

@compras.route('/actualizar/<int:id>', methods=['POST'])
@login_required
@role_required(1, 3)
def actualizar(id):
    try:
        _asegurar_esquema_compras()
        compra = Compra.query.get(id)

        if not compra:
            flash("Compra no encontrada", "danger")
            return redirect(url_for('compras.index'))

        _aplicar_datos_generales_compra(compra, request.form, usar_hora_actual=True)

        aplicar_cambios_compra(compra, request.form, permitir_editar_cantidad=(current_user.id_rol == 1))

        db.session.commit()

        flash("Compra actualizada correctamente", "success")
        return redirect(url_for('compras.index'))

    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")
        return redirect(url_for('compras.index'))
    
@compras.route('/completar/<int:id>', methods=['POST'])
@login_required
@role_required(1, 3)
def completar(id):
    try:
        _asegurar_esquema_compras()
        compra = Compra.query.get(id)

        if not compra:
            flash("Compra no encontrada", "danger")
            return redirect(url_for('compras.index'))

        _aplicar_datos_generales_compra(compra, request.form, usar_hora_actual=True)

        ok_requisitos, msg_requisitos = _validar_requisitos_recepcion(compra)
        if not ok_requisitos:
            db.session.rollback()
            flash(msg_requisitos, "warning")
            return redirect(url_for('compras.ver', id=id))

    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")
        return redirect(url_for('compras.ver', id=id))

    ok, msg = completar_compra(id, request.form, permitir_editar_cantidad=(current_user.id_rol == 1))

    if ok:
        compra = Compra.query.get(id)
        if compra:
            _registrar_log_entrada_almacen(compra, current_user.id_usuario)
        flash(msg, "success")
    else:
        flash(msg, "danger")

    return redirect(url_for('compras.ver', id=id))


@compras.route('/alerta/<int:id_materia>', methods=['GET'])
@login_required
@role_required(1, 2, 3)
def crear_desde_alerta(id_materia):
    session['compra_alerta_autorizada'] = True
    flash('Selecciona la materia de la alerta y agrega otras materias faltantes para producción.', 'info')
    return redirect(url_for('compras.crear', id_materia=id_materia))


@compras.route('/detalle/<int:id_compra>/<int:id_detalle>', methods=['POST'])
@login_required
@role_required(1, 3)
def recibir_detalle(id_compra, id_detalle):
    try:
        compra = Compra.query.get(id_compra)
        if not compra:
            flash('Compra no encontrada', 'danger')
            return redirect(url_for('compras.index'))

        _aplicar_datos_generales_compra(compra, request.form, usar_hora_actual=True)
        ok_requisitos, msg_requisitos = _validar_requisitos_recepcion(compra)
        if not ok_requisitos:
            db.session.rollback()
            flash(msg_requisitos, 'warning')
            return redirect(url_for('compras.index'))
    except Exception as e:
        db.session.rollback()
        flash(str(e), 'danger')
        return redirect(url_for('compras.index'))

    ok, msg = recibir_detalle_compra(id_compra, id_detalle, request.form)

    if ok:
        compra = Compra.query.get(id_compra)
        if compra:
            _registrar_log_entrada_almacen(compra, current_user.id_usuario)
        flash(msg, 'success')
    else:
        flash(msg, 'danger')

    return redirect(url_for('compras.index'))


@compras.route('/eliminar/<int:id>', methods=['POST'])
@login_required
@role_required(1)
def eliminar(id):
    ok, msg = eliminar_solicitud_compra(id)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('compras.index'))