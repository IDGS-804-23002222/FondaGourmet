from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash
from forms import ClienteForm
from app.extensions import db, app, user_datastore
from app.models import Usuario, Persona
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required
from flask_security.utils import login_user, logout_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('auth/login.html', form=form)

@auth_bp.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')
    remember  = True if request.form.get('remember') else False
        
    user = Usuario.query.filter_by(username=username).first()
    persona = Persona.query.filter_by(correo=correo).first()
    
    # 1. Caso fallido 
    if not user or not check_password_hash(user.contrasena, contrasena) or not persona:
        current_app.logger.warning(f"Intento de inicio de sesión fallido para username: {username}, correo: {correo}")
        flash('Nombre de usuario, correo y/o contraseña incorrectos.', 'danger')
        return redirect(url_for('auth.login'))
    
    # 2. Caso exitoso
    current_app.logger.info(f"Inicio de sesión exitoso para username: {username}, correo: {correo}")
    login_user(user, remember=remember)
    
    # Forzar escritura en el log para asegurar que se registre antes de redirigir
    for handler in current_app.logger.handlers:
        handler.flush()
    
    rol = user.id_rol
    if rol == 'Cocinero':
        flash(f'Bienvenido, {persona.nombre}. Redirigiendo a la sección de producción...', 'success')
        return redirect(url_for('produccion.index'))
    
    elif rol == 'Administrador' or rol == 'Dueño':
        flash(f'Bienvenido, {persona.nombre}. Redirigiendo al dashboard...', 'success')
        return redirect(url_for('dashboard.index'))
    
    elif rol == 'Cajero':
        flash(f'Bienvenido, {persona.nombre}. Redirigiendo a la sección de ventas...', 'success')
        return redirect(url_for('ventas.index'))
    
    elif rol == 'Cliente':
        flash(f'Bienvenido, {persona.nombre}. Redirigiendo a la sección de menú...', 'success')
        return redirect(url_for('fonda.index'))
    else:
        current_app.logger.error(f"Rol de usuario no reconocido para username: {username}, correo: {correo}, rol: {rol}")
        flash('Rol de usuario no reconocido.', 'danger')
        return redirect(url_for('auth.login'))

# Ruta de registro para cuenta de clientes
@auth_bp.route('/cuenta', methods=['GET', 'POST'])
def cuenta():
    return render_template('cuenta/registrar.html')

@auth_bp.route('/cuenta/registrar', methods=['POST'])
def registrar():
    form = ClienteForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            existePersona = Persona.query.filter((Persona.correo == form.correo.data) | (Persona.telefono == form.telefono.data)).first()
            existeUsuario = Usuario.query.filter_by(username=form.username.data).first()
            
            if existePersona:
                flash('El correo o teléfono ya existe. Por favor, elija otro.', 'danger')
                return render_template('cuenta/registrar.html', form=form)
            
            if existeUsuario:
                flash('El nombre de usuario ya existe. Por favor, elija otro.', 'danger')
                return render_template('cuenta/registrar.html', form=form)
            
             # Crear la persona
            persona = Persona(
                nombre=form.nombre.data,
                apellido_p=form.apellido_p.data,
                apellido_m=form.apellido_m.data,
                telefono=form.telefono.data,
                correo=form.correo.data,
                direccion=form.direccion.data
            )
            
            db.session.add(persona)
            db.session.flush()
            
            # Crear el usuario                
            usuario = Usuario(
                username=form.username.data,
                contrasena=generate_password_hash(form.contrasena.data),
                id_rol='Cliente'
            )
            db.session.add(usuario)
            db.session.commit()
            
            #Crear el cliente
            cliente = Cliente(
                id_persona=persona.id,
                id_usuario=usuario.id
            )
            db.session.add(cliente)
            db.session.commit()
            
            current_app.logger.info(f"Cuenta de cliente creada exitosamente para username: {form.username.data}, correo: {form.correo.data}")
            user_datastore.create_user(username=form.username.data, contrasena=generate_password_hash(form.contrasena.data), id_rol='Cliente')
            flash('Cuenta de cliente creada exitosamente. Por favor, inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la cuenta: {str(e)}', 'danger')
            current_app.logger.error(f"Error al crear cuenta para username: {form.username.data}, correo: {form.correo.data}")
    return render_template('cuenta/registrar.html', form=form)
        

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('auth.login'))