from . import auth
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, login_user, logout_user, current_user
from models import db, Usuario
from forms import LoginForm

# ====================== LOGIN ======================
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

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('index'))