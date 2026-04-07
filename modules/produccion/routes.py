from . import produccion
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from utils.security import role_required
from .services import (
    obtener_producciones,
    crear_produccion,
    cambiar_estado_produccion,
    iniciar_produccion,
    completar_produccion,
    cancelar_produccion
)

@produccion.route('/', methods=['GET'])
@login_required
@role_required(2)
def index():
    producciones, error = obtener_producciones()

    if error:
        flash("Error al cargar producción", "danger")
        return redirect(url_for('productos.index'))

    return render_template('produccion/index.html', producciones=producciones)


@produccion.route('/crear/<int:id_pedido>')
@login_required
def crear(id_pedido):
    exito, msg = crear_produccion(id_pedido)
    flash(msg, "success" if exito else "danger")
    return redirect(url_for('produccion.index'))


@produccion.route('/iniciar/<int:id>')
@login_required
def iniciar(id):
    exito, msg = cambiar_estado_produccion(id, "en_proceso")
    flash(msg, "success" if exito else "danger")
    return redirect(url_for('produccion.index'))


@produccion.route('/completar/<int:id>')
@login_required
def completar(id):
    exito, msg = cambiar_estado_produccion(id, "completada")
    flash(msg, "success" if exito else "danger")
    return redirect(url_for('produccion.index'))


@produccion.route('/cancelar/<int:id>')
@login_required
def cancelar(id):
    exito, msg = cambiar_estado_produccion(id, "cancelada")
    flash(msg, "success" if exito else "danger")
    return redirect(url_for('produccion.index'))

@produccion.route('/iniciar/<int:id>', methods=['POST'])
@login_required
def iniciar_produccion(id):
    exito, msg = iniciar_produccion(id)
    flash(msg, "success" if exito else "danger")
    return redirect(url_for('produccion.index'))

@produccion.route('/completar/<int:id>', methods=['POST'])
@login_required
def completar_produccion(id):
    exito, msg = completar_produccion(id)
    flash(msg, "success" if exito else "danger")
    return redirect(url_for('produccion.index'))

@produccion.route('/cancelar/<int:id>', methods=['POST'])
@login_required
def cancelar_produccion(id):
    exito, msg = cancelar_produccion(id)
    flash(msg, "success" if exito else "danger")
    return redirect(url_for('produccion.index'))