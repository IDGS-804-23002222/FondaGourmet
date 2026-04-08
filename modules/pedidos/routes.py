from . import pedidos
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from utils.security import role_required
from models import db, Pedido, DetallePedido, Producto, Cliente
from datetime import datetime
from .services import (
    obtener_pedidos, obtener_pedido, obtener_detalles_pedido, completar_pedido, cancelar_pedido,
    crear_pedido_manual, editar_pedido_propio
)

@pedidos.route('/')
@login_required
@role_required(3)
def index():
    pedidos, error = obtener_pedidos()
    productos = Producto.query.all()
    clientes = Cliente.query.all()
    if error:
        current_app.logger.error(f"Error al cargar pedidos: {error}")
        flash("Error al cargar los pedidos", "danger")
        return redirect(url_for('produccion.index'))

    hoy = datetime.now().date()
    pedidos_pendientes = sum(1 for pedido in pedidos if pedido.get('estado') == 'Pendiente')
    pedidos_en_proceso = sum(1 for pedido in pedidos if pedido.get('estado') == 'En Proceso')
    pedidos_produccion_completada = sum(
        1
        for pedido in pedidos
        if (
            pedido.get('estado') == 'Producido'
            or (pedido.get('estado') == 'Completado' and pedido.get('requiere_produccion'))
        )
    )
    pedidos_completados_hoy = sum(
        1
        for pedido in pedidos
        if pedido.get('estado') in ('Completado', 'Producido')
        and (
            (pedido.get('fecha_entrega') and pedido['fecha_entrega'].date() == hoy)
            or (pedido.get('fecha') and pedido['fecha'].date() == hoy)
        )
    )

    return render_template(
        'pedidos/index.html',
        pedidos=pedidos,
        productos=productos,
        clientes=clientes,
        pedidos_pendientes=pedidos_pendientes,
        pedidos_en_proceso=pedidos_en_proceso,
        pedidos_produccion_completada=pedidos_produccion_completada,
        pedidos_completados_hoy=pedidos_completados_hoy,
    )


@pedidos.route('/mis_pedidos')
@login_required
@role_required(4)
def mis_pedidos():
    id_cliente = current_user.cliente.id_cliente
    pedidos, error = obtener_pedido(id_cliente)

    if error:
        current_app.logger.error(f"Error al cargar pedidos: {error}")
        flash("Error al cargar los pedidos", "danger")
        return redirect(url_for('tienda.menu'))

    return render_template('pedidos/mis_pedidos.html', pedidos=pedidos)

@pedidos.route('/detalles/<int:id_pedido>')
@login_required
@role_required(3, 4)
def ver_detalles_pedido(id_pedido):

    pedido = Pedido.query.get(id_pedido)

    if not pedido:
        flash("Pedido no encontrado", "danger")
        return redirect(url_for('pedidos.mis_pedidos'))

    if current_user.id_rol == 4 and pedido.id_cliente != current_user.cliente.id_cliente:
        flash("No tienes permiso para ver este pedido", "danger")
        return redirect(url_for('pedidos.mis_pedidos'))

    return render_template('pedidos/detalles_pedido.html', pedido=pedido)

from flask import request, redirect, url_for, flash
from flask_login import current_user
from .services import completar_o_producir

@pedidos.route('/procesar', methods=['POST'])
@login_required
@role_required(3)
def procesar():

    id_pedido = request.form.get('id_pedido')
    fecha_necesaria = request.form.get('fecha_necesaria')

    exito, mensaje = completar_o_producir(id_pedido, current_user.id_usuario, fecha_necesaria)

    if exito:
        if "producción" in mensaje:
            flash(mensaje, "warning")  # 🔶 aviso
        else:
            flash(mensaje, "success")  # 🟢 éxito
    else:
        flash(mensaje, "danger")

    return redirect(url_for('pedidos.index'))


@pedidos.route('/crear', methods=['POST'])
@login_required
@role_required(3)
def crear():
    id_cliente = request.form.get('id_cliente')
    metodo_pago = request.form.get('metodo_pago')
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
            'cantidad': cantidades[idx] if idx < len(cantidades) else None
        })

    exito, mensaje = crear_pedido_manual(
        id_cliente,
        productos,
        metodo_pago,
        current_user.id_usuario,
        datos_tarjeta=datos_tarjeta,
    )
    flash(mensaje, 'success' if exito else 'danger')

    return redirect(url_for('pedidos.index'))
    
@pedidos.route('/cancelar/<int:id_pedido>', methods=['POST'])
@login_required
@role_required(3, 4)
def cancelar(id_pedido):
    if current_user.id_rol == 4:
        pedido = Pedido.query.get(id_pedido)
        if not pedido or pedido.id_cliente != current_user.cliente.id_cliente:
            return {"success": False, "message": "No tienes permiso para cancelar este pedido"}, 403

    success, message = cancelar_pedido(id_pedido)

    if success:
        return {"success": True, "message": message}
    else:
        return {"success": False, "message": message}, 400


@pedidos.route('/editar/<int:id_pedido>', methods=['GET', 'POST'])
@login_required
@role_required(4)
def editar(id_pedido):
    pedido = Pedido.query.get(id_pedido)

    if not pedido or pedido.id_cliente != current_user.cliente.id_cliente:
        flash("No tienes permiso para editar este pedido", "danger")
        return redirect(url_for('pedidos.mis_pedidos'))

    if pedido.estado != 'Pendiente':
        flash("Solo puedes editar pedidos pendientes", "warning")
        return redirect(url_for('pedidos.mis_pedidos'))

    if request.method == 'POST':
        ids_producto = request.form.getlist('id_producto[]')
        cantidades = request.form.getlist('cantidad[]')
        metodo_pago = request.form.get('metodo_pago')

        productos = []
        for idx in range(len(ids_producto)):
            productos.append({
                'id_producto': ids_producto[idx],
                'cantidad': cantidades[idx] if idx < len(cantidades) else None
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