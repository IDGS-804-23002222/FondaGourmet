from datetime import datetime, timedelta

from flask import current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from . import pedidos
from models import Cliente, Pedido, Producto
from utils.security import role_required
from .services import (
    cancelar_pedido,
    completar_o_producir,
    crear_pedido_manual,
    editar_pedido_propio,
    obtener_detalles_pedido,
    obtener_pedido,
    obtener_pedidos,
    procesar_pago_pedido,
    registrar_calificacion_pedido,
)


@pedidos.route('/')
@login_required
@role_required(1, 3)
def index():
    pedidos_lista, error = obtener_pedidos()
    productos = Producto.query.filter_by(estado=True).order_by(Producto.nombre.asc()).all()
    clientes = Cliente.query.all()

    if error:
        current_app.logger.error(f'Error al cargar pedidos: {error}')
        flash('Error al cargar los pedidos', 'danger')
        return redirect(url_for('dashboard.index'))

    hoy = datetime.now().date()
    pedidos_pendientes = sum(1 for pedido in pedidos_lista if (pedido.get('estado_pago') or '').lower() == 'pendiente')
    pedidos_pagados = sum(1 for pedido in pedidos_lista if (pedido.get('estado_pago') or '').lower() == 'pagado')
    pedidos_cancelados = sum(1 for pedido in pedidos_lista if (pedido.get('estado_pago') or '').lower() == 'cancelado')
    inicio = datetime.combine(hoy, datetime.min.time())
    fin = inicio + timedelta(days=1)
    pedidos_completados_hoy = (
        Pedido.query
        .filter(
            Pedido.estado.in_(['Completado', 'Producido']),
            func.coalesce(Pedido.fecha_entrega, Pedido.fecha) >= inicio,
            func.coalesce(Pedido.fecha_entrega, Pedido.fecha) < fin,
        )
        .count()
    )

    return render_template(
        'pedidos/pedidos.html',
        pedidos=pedidos_lista,
        productos=productos,
        clientes=clientes,
        pedidos_pendientes=pedidos_pendientes,
        pedidos_pagados=pedidos_pagados,
        pedidos_cancelados=pedidos_cancelados,
        pedidos_completados_hoy=pedidos_completados_hoy,
    )


@pedidos.route('/mis_pedidos')
@login_required
@role_required(4)
def mis_pedidos():
    id_cliente = current_user.cliente.id_cliente
    pedidos_lista, error = obtener_pedido(id_cliente)

    if error:
        current_app.logger.error(f'Error al cargar pedidos: {error}')
        flash('Error al cargar los pedidos', 'danger')
        return redirect(url_for('tienda.menu'))

    return render_template('pedidos/mis_pedidos.html', pedidos=pedidos_lista)


@pedidos.route('/detalles/<int:id_pedido>')
@login_required
@role_required(1, 3, 4)
def ver_detalles_pedido(id_pedido):
    pedido = Pedido.query.get(id_pedido)

    if not pedido:
        flash('Pedido no encontrado', 'danger')
        return redirect(url_for('pedidos.mis_pedidos'))

    if current_user.id_rol == 4 and (not current_user.cliente or pedido.id_cliente != current_user.cliente.id_cliente):
        flash('No tienes permiso para ver este pedido', 'danger')
        return redirect(url_for('pedidos.mis_pedidos'))

    return render_template('pedidos/detalles_pedido.html', pedido=pedido)


@pedidos.route('/procesar', methods=['POST'])
@login_required
@role_required(1, 3)
def procesar():
    id_pedido = request.form.get('id_pedido')
    fecha_necesaria = request.form.get('fecha_necesaria')
    metodo_pago = request.form.get('metodo_pago')
    datos_tarjeta = {
        'numero_tarjeta': request.form.get('numero_tarjeta', ''),
        'titular_tarjeta': request.form.get('titular_tarjeta', ''),
        'vencimiento_tarjeta': request.form.get('vencimiento_tarjeta', ''),
        'cvv_tarjeta': request.form.get('cvv_tarjeta', ''),
    }

    exito, mensaje = completar_o_producir(
        id_pedido,
        current_user.id_usuario,
        fecha_necesaria,
        metodo_pago=metodo_pago,
        datos_tarjeta=datos_tarjeta,
    )

    if exito:
        flash(mensaje, 'success' if 'completado' in (mensaje or '').lower() else 'warning')
    else:
        flash(mensaje, 'danger')

    return redirect(url_for('pedidos.index'))


@pedidos.route('/pagar/<int:id_pedido>', methods=['POST'])
@login_required
@role_required(1, 3, 4)
def pagar(id_pedido):
    metodo_pago = request.form.get('metodo_pago')
    datos_tarjeta = {
        'numero_tarjeta': request.form.get('numero_tarjeta', ''),
        'titular_tarjeta': request.form.get('titular_tarjeta', ''),
        'vencimiento_tarjeta': request.form.get('vencimiento_tarjeta', ''),
        'cvv_tarjeta': request.form.get('cvv_tarjeta', ''),
    }

    exito, mensaje = procesar_pago_pedido(
        id_pedido=id_pedido,
        id_usuario=current_user.id_usuario,
        metodo_pago=metodo_pago,
        datos_tarjeta=datos_tarjeta,
    )
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('pedidos.ticket', id_pedido=id_pedido))


@pedidos.route('/ticket/<int:id_pedido>')
@login_required
@role_required(1, 3, 4)
def ticket(id_pedido):
    pedido = Pedido.query.get(id_pedido)
    if not pedido:
        flash('Pedido no encontrado', 'danger')
        return redirect(url_for('pedidos.index'))

    if current_user.id_rol == 4 and (not current_user.cliente or pedido.id_cliente != current_user.cliente.id_cliente):
        flash('No tienes permiso para ver este ticket', 'danger')
        return redirect(url_for('pedidos.mis_pedidos'))

    if (pedido.estado_pago or '').strip().lower() != 'pagado':
        flash('El ticket solo está disponible cuando el pedido está pagado', 'warning')
        return redirect(url_for('pedidos.ver_detalles_pedido', id_pedido=id_pedido))

    return render_template('pedidos/detalles_pedido.html', pedido=pedido)


@pedidos.route('/calificar/<int:id_pedido>', methods=['POST'])
@login_required
@role_required(4)
def calificar_servicio(id_pedido):
    pedido = Pedido.query.get(id_pedido)
    if not pedido:
        return jsonify({'success': False, 'message': 'Pedido no encontrado'}), 404

    if not current_user.cliente or pedido.id_cliente != current_user.cliente.id_cliente:
        return jsonify({'success': False, 'message': 'No tienes permiso para calificar este pedido'}), 403

    if (pedido.estado_pago or '').strip().lower() != 'pagado':
        return jsonify({'success': False, 'message': 'Solo puedes calificar pedidos pagados'}), 400

    data = request.get_json(silent=True) or {}

    try:
        calificacion = int(data.get('calificacion', 0))
    except (TypeError, ValueError):
        calificacion = 0

    if calificacion < 1 or calificacion > 5:
        return jsonify({'success': False, 'message': 'La calificación general debe estar entre 1 y 5'}), 400

    comentario = (data.get('comentario') or '').strip() or 'Sin comentario'
    productos = data.get('productos') or []
    if not isinstance(productos, list) or not productos:
        return jsonify({'success': False, 'message': 'Debes calificar al menos un producto'}), 400

    productos_normalizados = []
    for producto in productos:
        if not isinstance(producto, dict):
            return jsonify({'success': False, 'message': 'Formato de productos inválido'}), 400

        nombre = (producto.get('nombre') or '').strip()
        try:
            calif_producto = int(producto.get('calificacion', 0))
        except (TypeError, ValueError):
            calif_producto = 0

        if not nombre or calif_producto < 1 or calif_producto > 5:
            return jsonify({'success': False, 'message': 'Cada producto debe tener nombre y calificación entre 1 y 5'}), 400

        productos_normalizados.append({
            'nombre': nombre,
            'calificacion': calif_producto,
        })

    exito, mensaje = registrar_calificacion_pedido(pedido, current_user.id_usuario, calificacion, comentario, productos_normalizados)
    status = 200 if exito else 500
    if not exito and 'permiso' in mensaje.lower():
        status = 403
    elif not exito and 'pedido' in mensaje.lower():
        status = 409

    return jsonify({'success': exito, 'message': mensaje}), status


@pedidos.route('/cancelar/<int:id_pedido>', methods=['POST'])
@login_required
@role_required(1, 3, 4)
def cancelar(id_pedido):
    if current_user.id_rol == 4:
        pedido = Pedido.query.get(id_pedido)
        if not pedido or not current_user.cliente or pedido.id_cliente != current_user.cliente.id_cliente:
            return {'success': False, 'message': 'No tienes permiso para cancelar este pedido'}, 403

    success, message = cancelar_pedido(id_pedido, current_user.id_usuario)
    if success:
        return {'success': True, 'message': message}
    return {'success': False, 'message': message}, 400


@pedidos.route('/crear', methods=['POST'])
@login_required
@role_required(1, 3)
def crear():
    id_cliente = request.form.get('id_cliente')
    metodo_pago = request.form.get('metodo_pago')
    fecha_necesaria = request.form.get('fecha_necesaria')
    datos_tarjeta = {
        'numero_tarjeta': request.form.get('numero_tarjeta', ''),
        'titular_tarjeta': request.form.get('titular_tarjeta', ''),
        'vencimiento_tarjeta': request.form.get('vencimiento_tarjeta', ''),
        'cvv_tarjeta': request.form.get('cvv_tarjeta', ''),
    }
    ids_producto = request.form.getlist('id_producto[]')
    cantidades = request.form.getlist('cantidad[]')

    productos = []
    for idx in range(len(ids_producto)):
        productos.append({
            'id_producto': ids_producto[idx],
            'cantidad': cantidades[idx] if idx < len(cantidades) else None,
        })

    exito, mensaje = crear_pedido_manual(
        id_cliente,
        productos,
        metodo_pago,
        current_user.id_usuario,
        datos_tarjeta=datos_tarjeta,
        fecha_necesaria=fecha_necesaria,
    )
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('pedidos.index'))


@pedidos.route('/editar/<int:id_pedido>', methods=['GET', 'POST'])
@login_required
@role_required(4)
def editar(id_pedido):
    pedido = Pedido.query.get(id_pedido)

    if not pedido or not current_user.cliente or pedido.id_cliente != current_user.cliente.id_cliente:
        flash('No tienes permiso para editar este pedido', 'danger')
        return redirect(url_for('pedidos.mis_pedidos'))

    if pedido.estado != 'Pendiente' or (pedido.estado_pago or 'Pendiente') != 'Pendiente':
        flash('Solo puedes editar pedidos pendientes', 'warning')
        return redirect(url_for('pedidos.mis_pedidos'))

    if request.method == 'POST':
        ids_producto = request.form.getlist('id_producto[]')
        cantidades = request.form.getlist('cantidad[]')
        metodo_pago = request.form.get('metodo_pago')

        productos = []
        for idx in range(len(ids_producto)):
            productos.append({
                'id_producto': ids_producto[idx],
                'cantidad': cantidades[idx] if idx < len(cantidades) else None,
            })

        exito, mensaje = editar_pedido_propio(
            id_pedido,
            current_user.cliente.id_cliente,
            productos,
            metodo_pago,
            current_user.id_usuario,
        )

        flash(mensaje, 'success' if exito else 'danger')
        return redirect(url_for('pedidos.mis_pedidos'))

    productos = Producto.query.filter_by(estado=True).order_by(Producto.nombre.asc()).all()
    return render_template('pedidos/editar_pedido.html', pedido=pedido, productos=productos)
