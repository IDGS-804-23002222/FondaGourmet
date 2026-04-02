from . import categorias
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from forms import CategoriaForm
from utils.security import role_required
from .services import (
    crear_categoria, obtener_categorias, filtrar_categorias, 
)
from models import db, Proveedor, Persona
from datetime import datetime

@categorias.route('/', methods=['GET'])
@login_required
@role_required(1)
def index():
    resultados, error = obtener_categorias()
    if error:
        current_app.logger.error(f"Error al obtener categorías: {str(error)}")
        flash(error, 'danger')
        return redirect(url_for('redirect_por_rol', role=current_user.rol_id))
    return render_template('categorias/index.html', categorias=resultados, name=current_user.username)

@categorias.route('/crear', methods=['GET', 'POST'])
@login_required
@role_required(1)
def crear():
    form = CategoriaForm()

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
