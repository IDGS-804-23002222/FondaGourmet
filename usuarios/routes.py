from . import usuarios
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from forms import RegistroUsuarioForm, RegistroClienteForm
from utils.security import role_required
from .services import (
    crear_cliente, crear_empleado, ver_usuarios, desactivar_usuario,
    activar_usuario, obtener_usuario, actualizar_usuario,
    obtener_roles, obtener_roles_nombres
)
from models import db, Usuario, Persona
from datetime import datetime

@usuarios.route('/lista', methods=['GET'])
@login_required
@role_required(1)
def listaUsuarios():
    resultados, error = ver_usuarios()
    if error:
        current_app.logger.error(f"Error al obtener usuarios: {str(error)}")
        flash(error, 'danger')
        return redirect(url_for('dashboard.index'))
    return render_template('usuarios/lista_usuarios.html', usuarios=resultados, name=current_user.username)

@usuarios.route('/crearCliente', methods=['GET', 'POST'])
def crearCliente():
    form = RegistroClienteForm()
    if form.validate_on_submit():
        exito, error = crear_cliente(form)

        if exito:
            current_app.logger.info(f"Cliente creado: {form.username.data}")    
            flash('Cuenta creada exitosamente', 'success')
            return redirect(url_for('auth.login'))
        else:
            current_app.logger.error(f"Error al crear cliente: {str(error)}")
            flash(error, 'danger')

    return render_template('usuarios/crear_cliente.html', form=form)

@usuarios.route('/crearEmpleado', methods=['GET', 'POST'])
@login_required
@role_required(1)
def crearEmpleado():
    form = RegistroUsuarioForm()

    roles, error = obtener_roles_nombres()
    if error:
        current_app.logger.error(f"Error al obtener roles: {str(error)}")
        flash(error, 'danger')
        roles = []

    if form.validate_on_submit():
        exito, error = crear_empleado(form)

        if exito:
            current_app.logger.info(f"Empleado creado: {form.username.data}")   
            flash('Empleado creado correctamente', 'success')
            return redirect(url_for('usuarios.listaUsuarios'))
        else:
            current_app.logger.error(f"Error al crear empleado: {str(error)}")
            flash(error, 'danger')

    return render_template('usuarios/crear_empleado.html', form=form)



@usuarios.route('/desactivar', methods=['POST'])
@login_required
@role_required(1)
def desactivarUsuario():
    id_usuario = request.form.get('id_usuario')
    usuario, error = obtener_usuario(id_usuario)
    exito, error = desactivar_usuario(id_usuario)
    if exito:
        current_app.logger.info(f"Usuario desactivado: {usuario.username}")
        flash('Usuario desactivado correctamente', 'success')
    else:        
        flash(error, 'danger')
    return redirect(url_for('usuarios.listaUsuarios'))

@usuarios.route('/activar', methods=['POST'])
@login_required
@role_required(1)
def activarUsuario():
    id_usuario = request.form.get('id_usuario')
    usuario, error = obtener_usuario(id_usuario)    
    exito, error = activar_usuario(id_usuario)
    if exito:
        current_app.logger.info(f"Usuario activado: {usuario.username}")
        flash('Usuario activado correctamente', 'success')
    else:        
        current_app.logger.error(f"Error al activar usuario: {str(error)}")
        flash(error, 'danger')
    return redirect(url_for('usuarios.listaUsuarios'))

@usuarios.route('/detalles')
@login_required
@role_required(1)
def detallesUsuario():
    id_usuario = request.args.get('id_usuario') 
    usuario, error = obtener_usuario(id_usuario)

    if error:
        current_app.logger.error(f"Error al obtener detalles del usuario: {str(error)}")
        flash(error, 'danger')
        return redirect(url_for('usuarios.listaUsuarios'))

    return render_template('usuarios/detalles_usuario.html', usuario=usuario)

@usuarios.route('/editar', methods=['GET', 'POST'])
@login_required
@role_required(1)
def editarUsuario():
    id_usuario = request.args.get('id_usuario')
    usuario, error = obtener_usuario(id_usuario)
    if error:
        current_app.logger.error(f"Error al obtener usuario: {str(error)}")
        flash(error, 'danger')
        return redirect(url_for('usuarios.listaUsuarios'))  
    if request.method == 'POST':
        exito, error = actualizar_usuario(id_usuario, request.form)

        if exito:
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('usuarios.listaUsuarios'))
        else:
            flash(error, 'danger')

    usuario, _ = obtener_usuario(id_usuario)

    return render_template('usuarios/editar_usuario.html', usuario=usuario)

@usuarios.route('/miperfil', methods=['GET', 'POST'])
@login_required
def miPerfil():
    usuario, error = obtener_usuario(current_user.id_usuario)

    if error:
        current_app.logger.error(f"Error al obtener perfil del usuario: {str(error)}")
        flash(error, 'danger')
        return redirect(url_for('dashboard.index'))
        
    return render_template('usuarios/mi_perfil.html', usuario=usuario)