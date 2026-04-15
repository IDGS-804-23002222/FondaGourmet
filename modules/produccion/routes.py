from . import produccion
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from utils.security import role_required
from datetime import datetime
from .services import (
    obtener_producciones,
    completar_produccion,
    ver_orden_produccion,
    crear_solicitud_produccion_desde_alerta
)
from models import Producto, Produccion, db


def iniciar_produccion(id_produccion):
    try:
        produccion_obj = Produccion.query.get(id_produccion)
        if not produccion_obj:
            return False, 'Produccion no encontrada'

        estado_actual = (produccion_obj.estado or '').strip()
        if estado_actual == 'Completada':
            return False, 'La produccion ya fue completada'
        if estado_actual == 'En Proceso':
            return True, 'La produccion ya estaba en proceso'

        produccion_obj.estado = 'En Proceso'
        db.session.commit()
        return True, 'Produccion iniciada correctamente'
    except Exception as exc:
        db.session.rollback()
        return False, str(exc)


def cancelar_produccion(id_produccion):
    try:
        produccion_obj = Produccion.query.get(id_produccion)
        if not produccion_obj:
            return False, 'Produccion no encontrada'

        estado_actual = (produccion_obj.estado or '').strip()
        if estado_actual == 'Completada':
            return False, 'No se puede cancelar una produccion completada'

        produccion_obj.estado = 'Solicitada'
        produccion_obj.fecha_completada = None
        db.session.commit()
        return True, 'Produccion regresada a estado Solicitada'
    except Exception as exc:
        db.session.rollback()
        return False, str(exc)

@produccion.route('/', methods=['GET'])
@login_required
@role_required(1, 2, 3)
def index():
    producciones, error = obtener_producciones()

    if error:
        flash("Error al cargar producción", "danger")
        return redirect(url_for('productos.index'))

    hoy = datetime.now().date()
    total_ordenes = len(producciones)
    ordenes_solicitadas = sum(1 for p in producciones if p.get('estado') == 'Solicitada')
    ordenes_en_proceso = sum(1 for p in producciones if p.get('estado') == 'En Proceso')
    ordenes_completadas_hoy = sum(
        1
        for p in producciones
        if p.get('estado') == 'Completada'
        and p.get('fecha_completada')
        and p['fecha_completada'].date() == hoy
    )

    return render_template(
        'produccion/index.html',
        producciones=producciones,
        total_ordenes=total_ordenes,
        ordenes_solicitadas=ordenes_solicitadas,
        ordenes_en_proceso=ordenes_en_proceso,
        ordenes_completadas_hoy=ordenes_completadas_hoy,
    )

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
@login_required
@role_required(1, 2, 3)
def iniciar(id):
    success, message = iniciar_produccion(id)

    if success:
        flash(message, "success")
    else:
        flash(message, "error")

    return redirect(url_for('produccion.index'))

@produccion.route('/completar/<int:id>')
@login_required
@role_required(1, 2, 3)
def completar(id):
    success, message = completar_produccion(id, id_usuario=current_user.id_usuario)

    if success:
        flash(message, "success")
    else:
        flash(message, "error")

    return redirect(url_for('produccion.index'))

@produccion.route('/cancelar/<int:id>')
@login_required
@role_required(1, 2, 3)
def cancelar(id):
    success, message = cancelar_produccion(id)

    if success:
        flash(message, "success")
    else:
        flash(message, "error")

    return redirect(url_for('produccion.index'))


@produccion.route('/alerta/<int:id_producto>', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def crear_desde_alerta(id_producto):
    producto = Producto.query.get(id_producto)

    if not producto:
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('caja.index'))

    if request.method == 'POST':
        cantidad = request.form.get('cantidad', 10)
        id_produccion, mensaje = crear_solicitud_produccion_desde_alerta(
            id_producto,
            current_user.id_usuario,
            cantidad=cantidad,
        )

        if id_produccion:
            flash(mensaje, 'success')
            return redirect(url_for('produccion.ver', id=id_produccion))

        flash(mensaje, 'danger')
        return redirect(url_for('produccion.crear_desde_alerta', id_producto=id_producto))

    stock_actual = float(producto.stock_actual or 0)
    stock_minimo = float(producto.stock_minimo or 0)
    faltante = max(0.0, stock_minimo - stock_actual)

    return render_template(
        'produccion/solicitud_alerta.html',
        producto=producto,
        cantidad_sugerida=10,
        faltante=faltante,
    )