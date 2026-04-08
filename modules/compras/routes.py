from . import compras
from flask import render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_required, current_user
from utils.security import role_required
from models import db, Compra, DetalleCompra, MateriaPrima, Proveedor
from .services import (
    obtener_compras, obtener_compra, completar_compra,
    aplicar_cambios_compra, crear_solicitud_compra_manual,
    obtener_materias_faltantes_produccion, obtener_materias_alerta_stock_bajo
)
from datetime import datetime


def _obtener_proveedores_relacionados_compra(compra):
    ids = {
        detalle.materia_prima.id_proveedor
        for detalle in compra.detalles
        if detalle.materia_prima and detalle.materia_prima.id_proveedor
    }
    if not ids:
        return []

    return Proveedor.query.filter(Proveedor.id_proveedor.in_(ids)).order_by(Proveedor.id_proveedor.asc()).all()


def _aplicar_datos_generales_compra(compra, form, usar_hora_actual=False):
    fecha_entrega = form.get('fecha_entrega')
    metodo_pago = form.get('metodo_pago')
    id_proveedor = form.get('id_proveedor', type=int)

    if fecha_entrega:
        fecha_base = datetime.strptime(fecha_entrega, "%Y-%m-%d")
        if usar_hora_actual:
            ahora = datetime.now()
            compra.fecha_entrega = datetime(
                fecha_base.year,
                fecha_base.month,
                fecha_base.day,
                ahora.hour,
                ahora.minute,
                ahora.second,
            )
        else:
            compra.fecha_entrega = fecha_base

    if metodo_pago:
        compra.metodo_pago = metodo_pago

    if id_proveedor:
        proveedores_permitidos = {p.id_proveedor for p in _obtener_proveedores_relacionados_compra(compra)}
        if proveedores_permitidos and id_proveedor not in proveedores_permitidos:
            raise ValueError("El proveedor no está relacionado con las materias primas de esta compra")
        compra.id_proveedor = id_proveedor

@compras.route('/')
@login_required
@role_required(1, 3)
def index():
    compras, error = obtener_compras()
    if error:
        current_app.logger.error(f"Error al cargar compras: {error}")
        flash("Error al cargar las compras", "danger")
        return redirect(url_for('pedidos.index'))

    hoy = datetime.now().date()
    compras_completadas_hoy = sum(
        1
        for compra in compras
        if compra['estado'] in ['Completada', 'Completado']
        and compra['fecha_entrega']
        and compra['fecha_entrega'].date() == hoy
    )
    compras_solicitadas = sum(1 for compra in compras if compra['estado'] == 'Solicitada')

    return render_template(
        'compras/index.html',
        compras=compras,
        compras_completadas_hoy=compras_completadas_hoy,
        compras_solicitadas=compras_solicitadas,
    )

@compras.route('/crear', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def crear():
    if current_user.id_rol == 2 and not session.get('compra_alerta_autorizada'):
        flash('Como cocinero solo puedes crear solicitudes de compra desde alertas.', 'warning')
        return redirect(url_for('produccion.index'))

    alerta_stock = request.args.get('alerta_stock', type=int)

    if request.method == 'POST':
        resultado, mensaje = crear_solicitud_compra_manual(request.form, current_user.id_usuario)

        if resultado:
            flash(mensaje, 'success')
            session.pop('compra_alerta_autorizada', None)

            if current_user.id_rol == 2:
                return redirect(url_for('produccion.index'))

            if isinstance(resultado, list):
                return redirect(url_for('compras.index'))
            return redirect(url_for('compras.ver', id=resultado))

        flash(mensaje, 'danger')
        return redirect(url_for('compras.crear'))

    id_materia_alerta = request.args.get('id_materia', type=int)

    materias = MateriaPrima.query.filter_by(estado=True).order_by(MateriaPrima.nombre.asc()).all()
    proveedores = Proveedor.query.filter_by(estado=True).order_by(Proveedor.id_proveedor.asc()).all()
    ids_materias = [m.id_materia for m in materias]
    materias_solicitadas = set()

    if ids_materias:
        filas_solicitadas = (
            db.session.query(DetalleCompra.id_materia)
            .join(Compra, Compra.id_compra == DetalleCompra.id_compra)
            .filter(
                Compra.estado.in_(['Solicitada', 'En Camino']),
                DetalleCompra.id_materia.in_(ids_materias)
            )
            .distinct()
            .all()
        )
        materias_solicitadas = {fila[0] for fila in filas_solicitadas}

    if alerta_stock:
        sugerencias = obtener_materias_alerta_stock_bajo(id_materia_alerta)
    elif id_materia_alerta:
        sugerencias = obtener_materias_alerta_stock_bajo(id_materia_alerta)
    else:
        sugerencias = obtener_materias_faltantes_produccion(id_materia_alerta)

    return render_template(
        'compras/crear.html',
        materias=materias,
        proveedores=proveedores,
        materias_solicitadas=materias_solicitadas,
        sugerencias=sugerencias,
        id_materia_alerta=id_materia_alerta,
        alerta_stock=bool(alerta_stock),
    )

@compras.route('/ver/<int:id>')
@login_required
@role_required(1, 3)
def ver(id):
    compra, error = obtener_compra(id)

    if not compra:
        flash("Compra no encontrada", "danger")
        return redirect(url_for('compras.index'))

    proveedores = _obtener_proveedores_relacionados_compra(Compra.query.get(id))
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')

    return render_template('compras/ver.html', compra=compra, proveedores=proveedores, fecha_hoy=fecha_hoy)

@compras.route('/actualizar/<int:id>', methods=['POST'])
@login_required
@role_required(1, 3)
def actualizar(id):
    try:
        compra = Compra.query.get(id)

        if not compra:
            flash("Compra no encontrada", "danger")
            return redirect(url_for('compras.index'))

        _aplicar_datos_generales_compra(compra, request.form, usar_hora_actual=True)

        aplicar_cambios_compra(compra, request.form)

        db.session.commit()

        flash("Compra actualizada correctamente", "success")
        return redirect(url_for('compras.index'))

    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")
        return redirect(url_for('compras.index'))
    
@compras.route('/completar/<int:id>', methods=['POST'])
@login_required
@role_required(1, 3)
def completar(id):
    try:
        compra = Compra.query.get(id)

        if not compra:
            flash("Compra no encontrada", "danger")
            return redirect(url_for('compras.index'))

        _aplicar_datos_generales_compra(compra, request.form)

    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")
        return redirect(url_for('compras.ver', id=id))

    ok, msg = completar_compra(id, request.form)

    if ok:
        flash(msg, "success")
    else:
        flash(msg, "danger")

    return redirect(url_for('compras.ver', id=id))


@compras.route('/alerta/<int:id_materia>', methods=['GET'])
@login_required
@role_required(1, 2, 3)
def crear_desde_alerta(id_materia):
    session['compra_alerta_autorizada'] = True
    flash('Selecciona la materia de la alerta y agrega otras materias faltantes para producción.', 'info')
    return redirect(url_for('compras.crear', id_materia=id_materia))