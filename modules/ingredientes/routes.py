from . import ingredientes
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from forms import RegistrarIngredienteForm, EditarIngredienteForm
from utils.security import role_required
from .services import (
    crear_ingrediente,
    obtener_ingredientes,
    filtrar_ingredientes,
    desactivar_ingrediente,
    activar_ingrediente,
    actualizar_ingrediente
)
from models import Categoria, Proveedor


@ingredientes.route('/', methods=['GET', 'POST'])
@login_required
@role_required(1)
def index():
    filtro = request.form.get('filtro')

    if filtro:
        ingredientes_list, error = filtrar_ingredientes(filtro)
    else:
        ingredientes_list, error = obtener_ingredientes()

    if error:
        current_app.logger.error(f"Error: {error}")
        flash(error, 'danger')
        return redirect(url_for('dashboard.index'))

    return render_template(
        'ingredientes/index.html',
        ingredientes=ingredientes_list,
        name=current_user.username
    )

@ingredientes.route('/crear', methods=['GET', 'POST'])
@login_required
@role_required(1)
def crear():
    form = RegistrarIngredienteForm()

    # cargar selects
    form.id_categoria.choices = [(c.id_categoria, c.nombre) for c in Categoria.query.all()]
    form.id_proveedor.choices = [(p.id_proveedor, p.persona.nombre) for p in Proveedor.query.all()]

    if form.validate_on_submit():
        exito, msg = crear_ingrediente(form)

        if exito:
            flash(msg, 'success')
            return redirect(url_for('ingredientes.index'))
        else:
            flash(msg, 'danger')

    return render_template('ingredientes/crear.html', form=form)

@ingredientes.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(1)
def editar(id):
    form = ActualizarIngredienteForm()

    # cargar selects
    form.id_categoria.choices = [(c.id_categoria, c.nombre) for c in Categoria.query.all()]
    form.id_proveedor.choices = [(p.id_proveedor, p.persona.nombre) for p in Proveedor.query.all()]

    if request.method == 'POST' and form.validate_on_submit():
        exito, msg = actualizar_ingrediente(id, form)

        if exito:
            flash(msg, 'success')
            return redirect(url_for('ingredientes.index'))
        else:
            flash(msg, 'danger')

    return render_template('ingredientes/editar.html', form=form)

@ingredientes.route('/desactivar', methods=['POST'])
@login_required
@role_required(1)
def desactivar():
    id_ingrediente = request.form.get('id')

    exito, msg = desactivar_ingrediente(id_ingrediente)

    if exito:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')

    return redirect(url_for('ingredientes.index'))

@ingredientes.route('/activar', methods=['POST'])
@login_required
@role_required(1)
def activar():
    id_ingrediente = request.form.get('id')

    exito, msg = activar_ingrediente(id_ingrediente)

    if exito:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')

    return redirect(url_for('ingredientes.index'))

@ingredientes.route('/detalle/<int:id>')
@login_required
@role_required(1)
def detalle(id):
    ingrediente = MateriaPrima.query.get_or_404(id)
    return render_template('ingredientes/detalle.html', ingrediente=ingrediente)
