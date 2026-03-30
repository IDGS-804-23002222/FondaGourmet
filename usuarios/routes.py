from . import usuarios
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from forms import RegistroUsuarioForm, RegistroClienteForm
from utils.security import role_required
from .services import crear_cliente, crear_empleado, ver_usuarios, desactivar_usuario, activar_usuario, obtener_usuario, actualizar_usuario, ver_mi_cuenta
from models import db, Usuario, Persona
from datetime import datetime

@usuarios.route('/')
@login_required
@role_required('Administrador')
def listaUsuarios():
    usuarios, error = ver_usuarios(None)
    if error:
        flash(error, 'danger')
        usuarios = []
    return render_template('usuarios/lista_usuarios.html', usuarios=usuarios, name=current_user.username)

@usuarios.route('/crearCliente', methods=['GET', 'POST'])
def crearCliente():
    form = RegistroClienteForm()
    if form.validate_on_submit():
        exito, error = crear_cliente(form)

        if exito:
            flash('Cuenta creada exitosamente', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(error, 'danger')

    return render_template('usuarios/crear_cliente.html', form=form)

@usuarios.route('/crearEmpleado', methods=['GET', 'POST'])
@login_required
@role_required('Administrador')
def crearEmpleado():
    form = RegistroUsuarioForm()

    if form.validate_on_submit():
        exito, error = crear_empleado(form)

        if exito:
            flash('Empleado creado correctamente', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash(error, 'danger')

    return render_template('usuarios/crear_empleado.html', form=form)



@usuarios.route('/desactivar', methods=['POST'])
@login_required
@role_required('Administrador')
def desactivarUsuario():
    id_usuario = request.form.get('id_usuario')
    usuario, error = obtener_usuario(id_usuario)
    exito, error = desactivar_usuario(id_usuario)
    if exito:
        flash('Usuario desactivado correctamente', 'success')
    else:        
        flash(error, 'danger')
    return redirect(url_for('usuarios.listaUsuarios'))

@usuarios.route('/activar', methods=['POST'])
@login_required
@role_required('Administrador')
def activarUsuario():
    id_usuario = request.form.get('id_usuario')
    usuario, error = obtener_usuario(id_usuario)    
    exito, error = activar_usuario(id_usuario)
    if exito:
        flash('Usuario activado correctamente', 'success')
    else:        
        flash(error, 'danger')
    return redirect(url_for('usuarios.listaUsuarios'))

@usuarios.route('/detalles')
@login_required
@role_required('Administrador')
def detallesUsuario():
    id_usuario = request.form.get('id_usuario') 
    usuario, error = obtener_usuario(id_usuario)

    if error:
        flash(error, 'danger')
        return redirect(url_for('usuarios.listaUsuarios'))

    return render_template('usuarios/detalles_usuario.html', usuario=usuario)

@usuarios.route('/editar', methods=['GET', 'POST'])
@login_required
@role_required('Administrador')
def editarUsuario():
    id_usuario = request.form.get('id_usuario')
    usuario, error = obtener_usuario(id_usuario)
    if error:
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
    # Un usuario solo puede ver su perfil, salvo administrador.
    if current_user.id_usuario != id_usuario and current_user.rol.nombre != 'Administrador':
        flash('No tienes permiso para ver este perfil.', 'warning')
        return redirect(url_for('dashboard.index'))

    usuario, error = ver_mi_cuenta(id_usuario)

    if error:
        flash(error, 'danger')
        if current_user.rol.nombre in ['Administrador']:
            return redirect(url_for('dashboard.index'))
        elif current_user.rol.nombre == 'Cajero':
            return redirect(url_for('ventas.index'))
        elif current_user.rol.nombre == 'Cocinero':
            return redirect(url_for('produccion.index'))
        elif current_user.rol.nombre == 'Cliente':
            return redirect(url_for('tienda.index'))
        else:
            return redirect(url_for('dashboard.index'))
        
    return render_template('usuarios/mi_perfil.html', usuario=usuario)