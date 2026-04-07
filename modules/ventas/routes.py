from . import ventas
from flask import render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from models import Producto, Cliente
from .services import(
    crear_venta, obtener_ventas
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

        ok, msg = crear_venta(
            current_user.id_usuario,
            metodo_pago,
            productos
        )

        return jsonify({"success": ok, "message": msg})

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