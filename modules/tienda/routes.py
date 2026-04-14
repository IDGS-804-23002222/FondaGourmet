from . import tienda
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Producto, Carrito, DetalleCarrito, Pedido
from utils.security import role_required
from .services import (
    obtener_menu, 
    agregar_producto_carrito, 
    obtener_carrito, 
    reducir_cantidad_carrito,
    agregar_cantidad_carrito,
    finalizar_pedido
)

@tienda.route('/', methods=['GET', 'POST'])
@login_required
@role_required(4)
def index():
    return render_template('tienda/index.html')

@tienda.route('/menu')
def menu():
    productos, error = obtener_menu()

    if error:
        current_app.logger.error(f"Error al cargar menú: {error}")
        flash("Error al cargar el menú", "danger")
        return redirect(url_for('tienda.index'))

    return render_template(
        'tienda/menu.html',
        productos=productos
    )
    
@tienda.route('/carrito')
@login_required
@role_required(3, 4)
def carrito():
    carrito, error = obtener_carrito()

    if error:
        current_app.logger.error(f"Error al cargar carrito: {error}")
        flash("Error al cargar el carrito", "danger")
        return redirect(url_for('tienda.menu'))

    return render_template('tienda/carrito.html', carrito=carrito)

@tienda.route('/agregar/<int:id>', methods=['GET'])
@login_required
@role_required(3, 4)
def agregar_carrito(id):
    exito, mensaje = agregar_producto_carrito(id)

    if exito:
        current_app.logger.info(f"Producto agregado: {id}")
        flash(mensaje, "success")
    else:
        current_app.logger.error(f"Error carrito: {mensaje}")
        flash(mensaje, "danger")

    return redirect(url_for('tienda.menu'))

@tienda.route('/reducir/<int:id>', methods=['GET'])
@login_required
@role_required(3, 4)
def reducir_cantidad(id):
    exito, mensaje = reducir_cantidad_carrito(id)

    if exito:
        current_app.logger.info(f"Cantidad reducida del carrito: {id}")
        flash(mensaje, "success")
        return redirect(url_for('tienda.carrito'))
    else:
        current_app.logger.error(f"Error al reducir cantidad del carrito: {mensaje}")
        flash(mensaje, "danger")

    return redirect(url_for('tienda.carrito'))

@tienda.route('/aumentar/<int:id>', methods=['GET'])
@login_required
@role_required(3, 4)
def aumentar_cantidad(id):
    exito, mensaje = agregar_cantidad_carrito(id)

    if exito:
        current_app.logger.info(f"Cantidad aumentada del carrito: {id}")
        flash(mensaje, "success")
        return redirect(url_for('tienda.carrito'))
    else:
        current_app.logger.error(f"Error al aumentar cantidad del carrito: {mensaje}")
        flash(mensaje, "danger")

    return redirect(url_for('tienda.carrito'))

@tienda.route('/actualizar_cantidad/', methods=['POST'])
@login_required
@role_required(3, 4)
def actualizar_cantidad(id):
    accion = request.json.get('accion')

    detalle = DetalleCarrito.query.get(id)

    if not detalle:
        return {"ok": False}

    if accion == "sumar":
        detalle.cantidad += 1
        
    elif accion == "restar":
        detalle.cantidad -= 1
        if detalle.cantidad <= 0:
            db.session.delete(detalle)
            db.session.commit()
            return {"ok": True,
                    "eliminado": True,
                    "cantidad": 0,
                    "subtotal": 0}
        return {"ok": True,
                "eliminado": False,
                "cantidad": detalle.cantidad,
                "subtotal": detalle.subtotal}
        
    detalle.cantidad = max(detalle.cantidad, 0)
    detalle.subtotal = detalle.cantidad * detalle.producto.precio

    carrito = detalle.carrito
    carrito.total = sum(d.subtotal for d in carrito.detalles)

    db.session.commit()

    return {"ok": True}

@tienda.route('/finalizar', methods=['POST'])
@login_required
@role_required(3, 4)
def finalizar_compra():
    metodo_pago = (request.form.get('metodo_pago') or 'Efectivo').strip()

    datos_tarjeta = {
        'numero_tarjeta': request.form.get('numero_tarjeta', ''),
        'titular_tarjeta': request.form.get('titular_tarjeta', ''),
        'vencimiento_tarjeta': request.form.get('vencimiento_tarjeta', ''),
        'cvv_tarjeta': request.form.get('cvv_tarjeta', ''),
    }

    exito, mensaje = finalizar_pedido(metodo_pago=metodo_pago, datos_tarjeta=datos_tarjeta)

    if not exito:
        flash(mensaje, "danger")
        return redirect(url_for('tienda.carrito'))

    flash("Pedido realizado con éxito 🧾", "success")
    return redirect(url_for('pedidos.mis_pedidos'))
