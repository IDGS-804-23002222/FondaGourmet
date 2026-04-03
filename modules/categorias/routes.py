from . import categorias
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from forms import RegistrarCategoriaForm, EditarCategoriaForm
from utils.security import role_required
from .services import (
    crear_categoria,
    obtener_categorias,
    filtrar_categorias,
    obtener_categoria,
    actualizar_categoria,
    desactivar_categoria,
    activar_categoria,
)


@categorias.route('/', methods=['GET'])
@login_required
@role_required(1)
def index():
    filtro = request.args.get('filtro')
    if filtro:
        resultados, error = filtrar_categorias(filtro)
    else:
        resultados, error = obtener_categorias()

    if error:
        current_app.logger.error(f"Error al obtener categorías: {str(error)}")
        flash(error, 'danger')
        return redirect(url_for('dashboard.index'))
    return render_template('categorias/index.html', categorias=resultados, name=current_user.username)

@categorias.route('/crear', methods=['GET', 'POST'])
@login_required
@role_required(1)
def crear():
    form = RegistrarCategoriaForm()

    if form.validate_on_submit():
        exito, error = crear_categoria(form)

        if exito:
            current_app.logger.info(f"Categoría creada: {form.nombre.data}")   
            flash('Categoría creada correctamente', 'success')
            return redirect(url_for('categorias.index'))
        else:
            current_app.logger.error(f"Error al crear categoría: {str(error)}")
            flash(error, 'danger')

    return render_template('categorias/crear.html', form=form)


@categorias.route('/detalles')
@login_required
@role_required(1)
def detalles():
    id_categoria = request.args.get('id_categoria')
    categoria, error = obtener_categoria(id_categoria)
    if error:
        flash(error, 'danger')
        return redirect(url_for('categorias.index'))
    return render_template('categorias/detalles.html', categoria=categoria)


@categorias.route('/editar', methods=['GET', 'POST'])
@login_required
@role_required(1)
def editar():
    form = EditarCategoriaForm()
    id_categoria = request.args.get('id_categoria') or request.form.get('id_categoria')
    if not id_categoria:
        flash('No se recibió la categoría a editar.', 'warning')
        return redirect(url_for('categorias.index'))

    categoria, error = obtener_categoria(id_categoria)
    if error:
        flash(error, 'danger')
        return redirect(url_for('categorias.index'))

    if request.method == 'GET':
        form.nombre.data = categoria.get('nombre')
        form.descripcion.data = categoria.get('descripcion')

    if request.method == 'POST' and form.validate_on_submit():
        exito, error = actualizar_categoria(id_categoria, form)
        if exito:
            flash('Categoría actualizada correctamente', 'success')
            return redirect(url_for('categorias.index'))
        flash(error, 'danger')

    return render_template('categorias/editar.html', form=form, categoria=categoria)


@categorias.route('/desactivar', methods=['POST'])
@login_required
@role_required(1)
def desactivar():
    id_categoria = request.form.get('id_categoria')
    exito, error = desactivar_categoria(id_categoria)
    if exito:
        flash('Categoría desactivada', 'success')
    else:
        flash(error, 'danger')
    return redirect(url_for('categorias.index'))


@categorias.route('/activar', methods=['POST'])
@login_required
@role_required(1)
def activar():
    id_categoria = request.form.get('id_categoria')
    exito, error = activar_categoria(id_categoria)
    if exito:
        flash('Categoría activada', 'success')
    else:
        flash(error, 'danger')
    return redirect(url_for('categorias.index'))
