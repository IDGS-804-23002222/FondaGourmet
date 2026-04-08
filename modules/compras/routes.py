from . import compras
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from utils.security import role_required
from models import db, Compra, DetalleCompra, MateriaPrima
from .services import (
    obtener_compras, obtener_compra, completar_compra
)
from datetime import datetime

@compras.route('/')
@login_required
@role_required(3)
def index():
    compras, error = obtener_compras()
    if error:
        current_app.logger.error(f"Error al cargar compras: {error}")
        flash("Error al cargar las compras", "danger")
        return redirect(url_for('pedidos.index'))

    return render_template('compras/index.html', compras=compras)

@compras.route('/ver/<int:id>')
@login_required
@role_required(3)
def ver(id):
    compra, error = obtener_compra(id)

    if not compra:
        flash("Compra no encontrada", "danger")
        return redirect(url_for('compras.index'))

    return render_template('compras/ver.html', compra=compra)

@compras.route('/actualizar/<int:id>', methods=['POST'])
@login_required
@role_required(3)
def actualizar(id):
    try:
        compra = Compra.query.get(id)

        if not compra:
            flash("Compra no encontrada", "danger")
            return redirect(url_for('compras.index'))

        fecha_entrega = request.form.get('fecha_entrega')
        metodo_pago = request.form.get('metodo_pago')

        # 🔥 actualizar datos generales
        if fecha_entrega:
            compra.fecha_entrega = datetime.strptime(fecha_entrega, "%Y-%m-%d")

        compra.metodo_pago = metodo_pago

        # 🔥 ACTUALIZAR PRECIOS POR DETALLE
        for d in compra.detalles:
            precio = request.form.get(f'precio_{d.id_detalle}')

            if precio:
                d.precio_u = float(precio)

        # 🔥 recalcular total
        total = 0
        for d in compra.detalles:
            total += d.cantidad * d.precio_u

        compra.total = total

        db.session.commit()

        flash("Compra actualizada correctamente", "success")
        return redirect(url_for('compras.ver', id=id))

    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")
        return redirect(url_for('compras.ver', id=id))
    
@compras.route('/completar/<int:id>', methods=['POST'])
@login_required
@role_required(3)
def completar(id):
    ok, msg = completar_compra(id)

    if ok:
        flash(msg, "success")
    else:
        flash(msg, "danger")

    return redirect(url_for('compras.ver', id=id))