from . import auth
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, login_user, logout_user, current_user
from models import db, Usuario
from forms import LoginForm, RegistroClienteForm
from .services import (
    crear_cliente, actualizar_mi_cuenta, ver_mi_cuenta
    )

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
      
    if form.validate_on_submit():
        remember = True if request.form.get('remember') else False
        
        # Buscar usuario
        user = Usuario.query.filter_by(username=form.username.data).first()
        
        # 1. CASO FALLIDO
        if not user or not user.check_password(form.contrasena.data):
            current_app.logger.warning(f"Intento de login fallido para usuario: {form.username.data}")
            flash("Usuario o contraseña incorrectos. Por favor, verifica tus credenciales.", "danger")
            return render_template('auth/login.html', form=form)
        
        # 2. CASO CUENTA INACTIVA
        if not user.estado:
            current_app.logger.warning(f"Intento de login para usuario inactivo: {form.username.data}")
            flash("Tu cuenta está inactiva. Por favor, contacta al administrador.", "warning")
            return render_template('auth/login.html', form=form)
        
        # 3. CASO EXITOSO
        current_app.logger.info(f"Login exitoso para usuario: {form.username.data}")
        
        # Usar login_user de flask_login (NO flask_security)
        login_user(user, remember=remember)
        
        flash(f'¡Bienvenido {user.username}!', 'success')
        
        return redirect_por_rol(user)
    
    if request.method == 'POST' and form.errors:
        for _, errors in form.errors.items():
            if errors:
                flash(errors[0], 'warning')
                break

    return render_template('auth/login.html', form=form)

def redirect_por_rol(user):
    """Función auxiliar para redirigir según el rol del usuario"""
    if user.rol.nombre in ['Administrador']:
        return redirect(url_for('dashboard.index'))
    elif user.rol.nombre == 'Cajero':
        return redirect(url_for('ventas.index'))
    elif user.rol.nombre == 'Cocinero':
        return redirect(url_for('produccion.index'))
    elif user.rol.nombre == 'Cliente':
        return redirect(url_for('tienda.index'))
    else:
        return redirect(url_for('dashboard.index'))

@auth.route('/crearCuenta', methods=['GET', 'POST'])
def crearCuenta():
    form = RegistroClienteForm()
    if form.validate_on_submit():
        exito, error = crear_cliente(form)
        if exito:
            flash('Cuenta creada exitosamente. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(error, 'danger')

    return render_template('auth/crear_cuenta.html', form=form)

@auth.route('/miPerfil')
@login_required
def mi_perfil():
    usuario = current_user
    if not usuario:
        current_app.logger.error("Usuario no encontrado en la base de datos.")
        flash("Error al cargar tu perfil. Por favor, intenta nuevamente.", "danger")
        return redirect(url_for('dashboard.index'))
    
    # Aquí podrías agregar más lógica para cargar información adicional del perfil si es necesario
    
    return render_template('auth/mi_perfil.html', usuario=usuario)

@auth.route('/editarPerfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    usuario = current_user
    if not usuario:
        current_app.logger.error("Usuario no encontrado en la base de datos.")
        flash("Error al cargar tu perfil. Por favor, intenta nuevamente.", "danger")
        return redirect(url_for('dashboard.index'))
    
    form = RegistroClienteForm(obj=usuario)
    
    if form.validate_on_submit():
        exito, error = actualizar_cliente(usuario.id_usuario, form)
        if exito:
            flash('Perfil actualizado correctamente.', 'success')
            return redirect(url_for('auth.mi_perfil'))
        else:
            flash(error, 'danger')  
    
        return render_template('auth/editar_perfil.html', form=form, usuario=usuario)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('index'))