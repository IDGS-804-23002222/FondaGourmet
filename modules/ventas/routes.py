from . import ventas
from flask import render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from models import Producto, Cliente
from .services import(
    crear_venta, obtener_ventas, obtener_detalle_venta
)
import traceback

# 📋 LISTADO
@ventas.route('/')
@login_required
def index():
    ventas, error = obtener_ventas()
    if error:
        current_app.logger.error(f"Error al cargar ventas: {error}")
        flash("Error al cargar las ventas", "danger")
    
    return render_template('ventas/index.html', ventas=ventas)


@ventas.route('/detalles/<int:id_venta>')
@login_required
def detalles(id_venta):
    venta, error = obtener_detalle_venta(id_venta)
    if error:
        current_app.logger.error(f"Error al cargar detalle de venta {id_venta}: {error}")
        flash(error, "danger")
        return redirect(url_for('ventas.index'))

    return render_template('ventas/detalles.html', venta=venta)


# 🧾 FORMULARIO
@ventas.route('/nueva')
@login_required
def nueva():
    productos = Producto.query.filter_by(estado=1).all()
    clientes = Cliente.query.all()
    return render_template('ventas/crear.html', productos=productos, clientes=clientes)


# 💾 GUARDAR VENTA
@ventas.route('/guardar', methods=['POST'])
@login_required
def guardar():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "message": "No se recibieron datos"}), 400

        metodo_pago = data.get("metodo_pago")
        productos = data.get("productos")

        if not metodo_pago:
            return jsonify({"success": False, "message": "Método de pago requerido"}), 400

        if not productos:
            return jsonify({"success": False, "message": "Agrega productos"}), 400

        ok, msg, id_venta = crear_venta(
            current_user.id_usuario,
            metodo_pago,
            productos
        )

        return jsonify({"success": ok, "message": msg, "id_venta": id_venta})

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500
        
@ventas.route('/eliminar', methods=['POST'])
@login_required
def eliminar():
    pass