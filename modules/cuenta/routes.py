from . import cuenta
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import logout_user, current_user, login_required
from forms import RegistroClienteForm, EditarPerfilForm
from .services import (
    crear_cliente, actualizar_mi_cuenta, ver_perfil, validar_datos, cargar_datos_usuario
    )
    

@cuenta.route('/perfil')
@login_required
def perfil():
    usuario, error = ver_perfil(current_user.id_usuario)
    if not usuario:
        current_app.logger.error("Usuario no encontrado en la base de datos.")
        flash("Error al cargar tu perfil. Por favor, intenta nuevamente.", "danger")
        return redirect(url_for('auth.redirigir'))
    return render_template('cuenta/perfil.html', usuario=usuario)
    
@cuenta.route('/crear', methods=['GET', 'POST'])
def crear():
    form = RegistroClienteForm()
    if form.validate_on_submit() and request.method == 'POST':
        exito, error = crear_cliente(form)
        if exito:
            current_app.logger.info(f"Cuenta creada para cliente: {form.username.data}")
            flash('Cuenta creada exitosamente. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            current_app.logger.error(f"Error al crear cuenta: {str(error)}")
            flash('Error al crear cuenta. Por favor, intenta nuevamente.', 'danger')
            return render_template('cuenta/crear.html', form=form)
    return render_template('cuenta/crear.html', form=form)

@cuenta.route('/editar', methods=['GET', 'POST'])
@login_required
def editar():
    usuario = current_user
    if not usuario:
        current_app.logger.error("Usuario no encontrado en la base de datos.")
        flash("Error al cargar tu perfil. Por favor, intenta nuevamente.", "danger")
        return redirect(url_for('auth.redirigir'))
    
    form = EditarPerfilForm()
    usuario, error = cargar_datos_usuario(usuario.id_usuario, form)
    if not usuario:
        current_app.logger.error("Error al cargar datos del usuario para edición.")
        flash("Error al cargar tu perfil. Por favor, intenta nuevamente.", "danger")
        return redirect(url_for('auth.redirigir'))    
    
    if request.method == 'GET':
        form.nombre.data = usuario.get('nombre')
        form.apellido_p.data = usuario.get('apellido_p')
        form.apellido_m.data = usuario.get('apellido_m')
        form.telefono.data = usuario.get('telefono')
        form.correo.data = usuario.get('correo')
        form.direccion.data = usuario.get('direccion')
        form.username.data = usuario.get('username')
        
    if request.method == 'POST' and form.validate_on_submit():
        exito, error = actualizar_mi_cuenta(usuario.id_usuario, form=request.form)
        if exito:
            current_app.logger.info(f"Perfil actualizado para cliente: {form.username.data}")
            flash('Perfil actualizado correctamente.', 'success')
            return redirect(url_for('cuenta.perfil'))
        else:
            current_app.logger.error(f"Error al actualizar perfil: {str(error)}")
            flash('Error al actualizar el perfil. Por favor, intenta nuevamente.', 'danger')
    return render_template('cuenta/editar.html', form=form, usuario=usuario)