from . import proveedores
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from forms import RegistroProveedorForm, EditarProveedorForm
from utils.security import role_required
from .services import (
    crear_proveedor, ver_proveedores, filtrar_proveedores, desactivar_proveedor,
    activar_proveedor, obtener_proveedor, actualizar_proveedor
)
from models import Proveedor

@proveedores.route('/', methods=['GET'])
@login_required
@role_required(1)
def index():
    q = (request.args.get('q') or '').strip()
    estado = (request.args.get('estado') or 'all').strip().lower()

    if q:
        proveedores_db, error = filtrar_proveedores(q)
        if error:
            current_app.logger.error(f"Error al filtrar proveedores: {str(error)}")
            flash(error, 'danger')
            return redirect(url_for('dashboard.index'))

        resultados = []
        for prov in proveedores_db:
            persona = prov.persona
            resultados.append({
                'id_proveedor': prov.id_proveedor,
                'nombre': persona.nombre if persona else None,
                'apellido_paterno': persona.apellido_p if persona else None,
                'apellido_materno': persona.apellido_m if persona else None,
                'telefono': persona.telefono if persona else None,
                'correo': persona.correo if persona else None,
                'categoria_proveedor': prov.categoria_proveedor.nombre if prov.categoria_proveedor else 'N/A',
                'estado_display': 'Activo' if prov.estado else 'Inactivo',
                'estado_bool': bool(prov.estado),
            })
    else:
        resultados, error = ver_proveedores()

    if error:
        current_app.logger.error(f"Error al obtener proveedores: {str(error)}")
        flash(error, 'danger')
        return redirect(url_for('dashboard.index'))

    if estado == 'activo':
        resultados = [p for p in resultados if p.get('estado_bool')]
    elif estado == 'inactivo':
        resultados = [p for p in resultados if not p.get('estado_bool')]

    return render_template(
        'proveedores/index.html',
        proveedores=resultados,
        name=current_user.username,
        q=q,
        estado=estado,
    )

@proveedores.route('/crear', methods=['GET', 'POST'])
@login_required
@role_required(1)
def crear():
    form = RegistroProveedorForm()

    if form.validate_on_submit():
        exito, error = crear_proveedor(form)

        if exito:
            current_app.logger.info(f"Proveedor creado: {form.nombre.data}")   
            flash('Proveedor creado correctamente', 'success')
            return redirect(url_for('proveedores.index'))
        else:
            current_app.logger.error(f"Error al crear proveedor: {str(error)}")
            flash(error, 'danger')

    return render_template('proveedores/crear.html', form=form)



@proveedores.route('/desactivar', methods=['POST'])
@login_required
@role_required(1)
def desactivar():
    id_proveedor = request.form.get('id_proveedor')

    exito, error = desactivar_proveedor(id_proveedor)

    if exito:
        current_app.logger.info(f"Proveedor desactivado: ID {id_proveedor}")
        flash('Proveedor desactivado', 'success')
    else:
        current_app.logger.error(f"Error al desactivar proveedor: {str(error)}")
        flash(error, 'danger')

    return redirect(url_for('proveedores.index'))


@proveedores.route('/desactivar/<int:id_proveedor>', methods=['POST'])
@login_required
@role_required(1)
def desactivar_por_id(id_proveedor):
    exito, error = desactivar_proveedor(id_proveedor)

    if exito:
        current_app.logger.info(f"Proveedor desactivado: ID {id_proveedor}")
        flash('Proveedor desactivado', 'success')
    else:
        current_app.logger.error(f"Error al desactivar proveedor: {str(error)}")
        flash(error, 'danger')

    return redirect(url_for('proveedores.index'))

@proveedores.route('/activar', methods=['POST'])
@login_required
@role_required(1)
def activar():
    id_proveedor = request.form.get('id_proveedor')

    exito, error = activar_proveedor(id_proveedor)

    if exito:
        current_app.logger.info(f"Proveedor activado: ID {id_proveedor}")
        flash('Proveedor activado', 'success')
    else:
        current_app.logger.error(f"Error al activar proveedor: {str(error)}")
        flash(error, 'danger')

    return redirect(url_for('proveedores.index'))


@proveedores.route('/activar/<int:id_proveedor>', methods=['POST'])
@login_required
@role_required(1)
def activar_por_id(id_proveedor):
    exito, error = activar_proveedor(id_proveedor)

    if exito:
        current_app.logger.info(f"Proveedor activado: ID {id_proveedor}")
        flash('Proveedor activado', 'success')
    else:
        current_app.logger.error(f"Error al activar proveedor: {str(error)}")
        flash(error, 'danger')

    return redirect(url_for('proveedores.index'))


@proveedores.route('/<int:id_proveedor>')
@login_required
@role_required(1)
def ver(id_proveedor):
    proveedor, error = obtener_proveedor(id_proveedor)

    if error:
        current_app.logger.error(f"Error al obtener detalles del proveedor: {str(error)}")
        flash(error, 'danger')
        return redirect(url_for('proveedores.index'))

    return render_template('proveedores/detalles.html', proveedor=proveedor)

@proveedores.route('/detalles')
@login_required
@role_required(1)
def detalles():
    id_proveedor = request.args.get('id_proveedor') 
    proveedor, error = obtener_proveedor(id_proveedor)

    if error:
        current_app.logger.error(f"Error al obtener detalles del proveedor: {str(error)}")
        flash(error, 'danger')
        return redirect(url_for('proveedores.index'))

    return render_template('proveedores/detalles.html', proveedor=proveedor)

@proveedores.route('/editar', methods=['GET', 'POST'])
@login_required
@role_required(1)
def editar():
    form = EditarProveedorForm()
    
    id_proveedor = request.args.get('id_proveedor') or request.form.get('id_proveedor')
    if not id_proveedor:
        flash('No se recibió el proveedor a editar.', 'warning')
        return redirect(url_for('proveedores.index'))

    proveedor, error = obtener_proveedor(id_proveedor)
    if error:
        current_app.logger.error(f"Error al obtener proveedor para edición: {str(error)}")
        flash(error, 'danger')
        return redirect(url_for('proveedores.index'))
     
    if request.method == 'GET':
        form.nombre.data = proveedor.get('nombre')
        form.apellido_p.data = proveedor.get('apellido_paterno')
        form.apellido_m.data = proveedor.get('apellido_materno')
        form.telefono.data = proveedor.get('telefono')
        form.correo.data = proveedor.get('correo')
        form.direccion.data = proveedor.get('direccion')
        form.id_categoria_proveedor.data = proveedor.get('id_categoria_proveedor')
    
    if request.method == 'POST' and form.validate_on_submit():
            exito, error = actualizar_proveedor(id_proveedor, request.form)

            if exito:
                current_app.logger.info(f"Proveedor actualizado: {form.nombre.data}")   
                flash('Proveedor actualizado correctamente', 'success')
                return redirect(url_for('proveedores.index'))
            else:
                current_app.logger.error(f"Error al actualizar proveedor: {str(error)}")
                flash(error, 'danger')
    
    return render_template('proveedores/editar.html', form=form, proveedor=proveedor)


@proveedores.route('/editar/<int:id_proveedor>', methods=['GET', 'POST'])
@login_required
@role_required(1)
def editar_por_id(id_proveedor):
    form = EditarProveedorForm()

    proveedor, error = obtener_proveedor(id_proveedor)
    if error:
        current_app.logger.error(f"Error al obtener proveedor para edición: {str(error)}")
        flash(error, 'danger')
        return redirect(url_for('proveedores.index'))

    if request.method == 'GET':
        form.nombre.data = proveedor.get('nombre')
        form.apellido_p.data = proveedor.get('apellido_paterno')
        form.apellido_m.data = proveedor.get('apellido_materno')
        form.telefono.data = proveedor.get('telefono')
        form.correo.data = proveedor.get('correo')
        form.direccion.data = proveedor.get('direccion')
        form.id_categoria_proveedor.data = proveedor.get('id_categoria_proveedor')

    if request.method == 'POST' and form.validate_on_submit():
        exito, error = actualizar_proveedor(id_proveedor, form)

        if exito:
            current_app.logger.info(f"Proveedor actualizado: {form.nombre.data}")
            flash('Proveedor actualizado correctamente', 'success')
            return redirect(url_for('proveedores.index'))

        current_app.logger.error(f"Error al actualizar proveedor: {str(error)}")
        flash(error, 'danger')

    return render_template('proveedores/editar.html', form=form, proveedor=proveedor)
