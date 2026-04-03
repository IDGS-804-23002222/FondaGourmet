from . import pedidos
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from utils.security import role_required
from models import db, Pedido, DetallePedido
from .services import (
    obtener_pedidos, obtener_detalles_pedido
)

@pedidos.route('/mis_pedidos')
@login_required
@role_required(4)
def mis_pedidos():
    id_cliente = current_user.cliente.id_cliente
    pedidos, error = obtener_pedidos(id_cliente)

    if error:
        current_app.logger.error(f"Error al cargar pedidos: {error}")
        flash("Error al cargar los pedidos", "danger")
        return redirect(url_for('tienda.index'))

    return render_template('pedidos/mis_pedidos.html', pedidos=pedidos)

@pedidos.route('/detalles/<int:id_pedido>')
@login_required
@role_required(2, 4)
def ver_detalles_pedido(id_pedido):

    pedido = Pedido.query.get(id_pedido)

    if not pedido:
        flash("Pedido no encontrado", "danger")
        return redirect(url_for('pedidos.mis_pedidos'))

    return render_template('pedidos/detalles_pedido.html', pedido=pedido)
