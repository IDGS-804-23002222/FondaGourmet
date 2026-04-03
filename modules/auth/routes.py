from . import auth
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, login_user, logout_user, current_user
from models import db, Usuario
from forms import LoginForm, RegistroClienteForm, EditarPerfilForm
from modules.cuenta.services import crear_cliente, actualizar_mi_cuenta, ver_perfil, cargar_datos_usuario


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
            current_app.logger.info(f"Cuenta creada para cliente: {form.username.data}")
            flash('Cuenta creada exitosamente. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            current_app.logger.error(f"Error al crear cuenta: {str(error)}")
            flash(error, 'danger')

    return render_template('cuenta/crear.html', form=form)

@auth.route('/miPerfil')
@login_required
def mi_perfil():
    usuario, error = ver_perfil(current_user.id_usuario)
    if not usuario:
        current_app.logger.error("Usuario no encontrado en la base de datos.")
        flash("Error al cargar tu perfil. Por favor, intenta nuevamente.", "danger")
        return redirect(url_for('dashboard.index'))

    return render_template('cuenta/perfil.html', usuario=usuario)

@auth.route('/editarPerfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    usuario = current_user
    if not usuario:
        current_app.logger.error("Usuario no encontrado en la base de datos.")
        flash("Error al cargar tu perfil. Por favor, intenta nuevamente.", "danger")
        return redirect(url_for('dashboard.index'))
    
    form = EditarPerfilForm()

    datos_usuario, error = cargar_datos_usuario(usuario.id_usuario, form)
    if not datos_usuario:
        current_app.logger.error(f"Error al cargar datos del perfil: {str(error)}")
        flash("No fue posible cargar tus datos para edición.", "danger")
        return redirect(url_for('cuenta.perfil'))

    if request.method == 'GET':
        form.nombre.data = datos_usuario.get('nombre')
        form.apellido_p.data = datos_usuario.get('apellido_p')
        form.apellido_m.data = datos_usuario.get('apellido_m')
        form.telefono.data = datos_usuario.get('telefono')
        form.correo.data = datos_usuario.get('correo')
        form.direccion.data = datos_usuario.get('direccion')
        form.username.data = datos_usuario.get('username')
    
    if form.validate_on_submit():
        exito, error = actualizar_mi_cuenta(usuario.id_usuario, request.form)
        if exito:
            current_app.logger.info(f"Perfil actualizado para cliente: {form.username.data}")
            flash('Perfil actualizado correctamente.', 'success')
            return redirect(url_for('cuenta.perfil'))
        else:
            flash(error, 'danger')  

    return render_template('cuenta/editar.html', form=form, usuario=datos_usuario)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('index'))

@auth.route('/redirigir')
@login_required
def redirigir():
    return redirect_por_rol(current_user)