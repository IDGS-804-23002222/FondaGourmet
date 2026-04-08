from . import produccion
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from utils.security import role_required
from .services import (
    obtener_producciones,
    completar_o_solicitar_compra,
    ver_orden_produccion,
    crear_solicitud_produccion_desde_alerta
)

@produccion.route('/', methods=['GET'])
@login_required
@role_required(1, 2, 3)
def index():
    producciones, error = obtener_producciones()

    if error:
        flash("Error al cargar producción", "danger")
        return redirect(url_for('productos.index'))

    return render_template('produccion/index.html', producciones=producciones)

@produccion.route('/ver/<int:id>')
@login_required
@role_required(1, 2, 3)
def ver(id):
    prod, error = ver_orden_produccion(id)

    if error:
        flash("Error al cargar producción", "danger")
        return redirect(url_for('produccion.index'))

    return render_template('produccion/ver.html', produccion=prod)
@produccion.route('/iniciar/<int:id>')
def iniciar(id):
    success, message = iniciar_produccion(id)

    if success:
        flash(message, "success")
    else:
        flash(message, "error")

    return redirect(url_for('produccion.index'))

@produccion.route('/completar/<int:id>')
def completar(id):
    success, message = completar_o_solicitar_compra(id, id_usuario=current_user.id_usuario)

    if success:
        flash(message, "success")
    else:
        flash(message, "error")

    return redirect(url_for('produccion.index'))

@produccion.route('/cancelar/<int:id>')
def cancelar(id):
    success, message = cancelar_produccion(id)

    if success:
        flash(message, "success")
    else:
        flash(message, "error")

    return redirect(url_for('produccion.index'))


@produccion.route('/alerta/<int:id_producto>', methods=['GET'])
@login_required
@role_required(1, 2, 3)
def crear_desde_alerta(id_producto):
    id_produccion, mensaje = crear_solicitud_produccion_desde_alerta(id_producto, current_user.id_usuario)

    if id_produccion:
        flash(mensaje, 'success')
        return redirect(url_for('produccion.ver', id=id_produccion))

    flash(mensaje, 'danger')
    return redirect(url_for('produccion.index'))