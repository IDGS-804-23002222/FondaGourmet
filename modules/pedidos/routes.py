from . import pedidos
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from utils.security import role_required
from models import db, Pedido, DetallePedido, Producto
from .services import (
    obtener_pedidos, obtener_pedido, obtener_detalles_pedido, solicitar_produccion, completar_pedido, cancelar_pedido
)

@pedidos.route('/')
@login_required
@role_required(3)
def index():
    pedidos, error = obtener_pedidos()
    productos = Producto.query.all()
    if error:
        current_app.logger.error(f"Error al cargar pedidos: {error}")
        flash("Error al cargar los pedidos", "danger")
        return redirect(url_for('produccion.index'))

    return render_template('pedidos/index.html', pedidos=pedidos, productos=productos)


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

    return render_template('pedidos/detalles_pedido.html', pedido=pedido)

from flask import request, redirect, url_for, flash
from flask_login import current_user
from .services import completar_o_producir

@pedidos.route('/procesar', methods=['POST'])
@login_required
@role_required(3)
def procesar():

    id_pedido = request.form.get('id_pedido')

    exito, mensaje = completar_o_producir(id_pedido, current_user.id_usuario)

    if exito:
        if "producción" in mensaje:
            flash(mensaje, "warning")  # 🔶 aviso
        else:
            flash(mensaje, "success")  # 🟢 éxito
    else:
        flash(mensaje, "danger")

    return redirect(url_for('pedidos.index'))
    
@pedidos.route('/solicitar_produccion/<int:id>')
@login_required
@role_required(3)
def solicitar_produccion(id):          
    exito, msg = solicitar_produccion(id)
    if exito:
        current_app.logger.info(f"Producción solicitada para pedido {id} exitosamente")
        flash(msg, "success")
    else:
        current_app.logger.error(f"Error al solicitar producción para pedido {id}: {msg}")
        flash(msg, "danger")
    return redirect(url_for('pedidos.index'))

@pedidos.route('/cancelar/<int:id_pedido>', methods=['POST'])
def cancelar(id_pedido):
    success, message = cancelar_pedido(id_pedido)

    if success:
        return {"success": True, "message": message}
    else:
        return {"success": False, "message": message}, 400