from . import auth
from flask import render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_required, login_user, logout_user, current_user
from models import db, Usuario
from forms import LoginForm, RegistroClienteForm, EditarPerfilForm, OTPVerificationForm
from modules.cuenta.services import crear_cliente, actualizar_mi_cuenta, ver_perfil, cargar_datos_usuario
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pyotp


OTP_SESSION_USER_KEY = 'otp_pending_user_id'
OTP_SESSION_SECRET_KEY = 'otp_totp_secret'
OTP_SESSION_REMEMBER_KEY = 'otp_pending_remember'


def _obtener_correo_usuario(user):
    if user and user.empleado and user.empleado.persona and user.empleado.persona.correo:
        return user.empleado.persona.correo
    if user and user.cliente and user.cliente.persona and user.cliente.persona.correo:
        return user.cliente.persona.correo
    return None


def _enviar_codigo_otp_por_correo(destinatario, codigo, username=None):
    servidor = current_app.config.get('MAIL_SERVER')
    puerto = current_app.config.get('MAIL_PORT')
    usa_tls = current_app.config.get('MAIL_USE_TLS')
    usuario = current_app.config.get('MAIL_USERNAME')
    password = current_app.config.get('MAIL_PASSWORD')
    remitente = current_app.config.get('MAIL_DEFAULT_SENDER')

    if not servidor or not puerto or not usuario or not password:
        raise ValueError('La configuracion de correo SMTP esta incompleta.')

    asunto = 'Tu codigo de verificacion - Casa Gourmet'
    cuerpo_texto = (
        'Casa Gourmet\n\n'
        f'Hola {username or "usuario"},\n\n'
        f'Tu codigo de verificacion es: {codigo}\n\n'
        'Este codigo expira en 5 minutos.\n'
        'Si no intentaste iniciar sesion, ignora este correo.'
    )

    cuerpo_html = render_template(
        'emails/otp_codigo.html',
        codigo=codigo,
        username=username or 'usuario',
        minutos_expiracion=5,
    )

    mensaje = MIMEMultipart('alternative')
    mensaje['Subject'] = asunto
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje.attach(MIMEText(cuerpo_texto, 'plain', 'utf-8'))
    mensaje.attach(MIMEText(cuerpo_html, 'html', 'utf-8'))

    smtp = smtplib.SMTP(servidor, puerto, timeout=15)
    try:
        if usa_tls:
            smtp.starttls()
        smtp.login(usuario, password)
        smtp.sendmail(remitente, [destinatario], mensaje.as_string())
    finally:
        smtp.quit()


def _limpiar_sesion_otp():
    session.pop(OTP_SESSION_USER_KEY, None)
    session.pop(OTP_SESSION_SECRET_KEY, None)
    session.pop(OTP_SESSION_REMEMBER_KEY, None)


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

        correo_destino = _obtener_correo_usuario(user)
        if not correo_destino:
            current_app.logger.error(f"Usuario sin correo configurado para 2FA: {user.username}")
            flash('No se encontro un correo asociado para verificacion en dos pasos.', 'danger')
            return render_template('auth/login.html', form=form)

        try:
            secreto = pyotp.random_base32()
            codigo = pyotp.TOTP(secreto, interval=300).now()
            _enviar_codigo_otp_por_correo(correo_destino, codigo, user.username)

            session[OTP_SESSION_USER_KEY] = user.id_usuario
            session[OTP_SESSION_SECRET_KEY] = secreto
            session[OTP_SESSION_REMEMBER_KEY] = remember

            flash('Te enviamos un codigo de verificacion a tu correo.', 'info')
            return redirect(url_for('auth.verificar_otp'))
        except Exception as e:
            current_app.logger.error(f"Error enviando OTP por correo: {str(e)}")
            flash('No fue posible enviar el codigo de verificacion. Intenta nuevamente.', 'danger')
            return render_template('auth/login.html', form=form)
    
    if request.method == 'POST' and form.errors:
        for _, errors in form.errors.items():
            if errors:
                flash(errors[0], 'warning')
                break

    return render_template('auth/login.html', form=form)


@auth.route('/verificar-otp', methods=['GET', 'POST'])
def verificar_otp():
    user_id = session.get(OTP_SESSION_USER_KEY)
    secreto = session.get(OTP_SESSION_SECRET_KEY)
    remember = bool(session.get(OTP_SESSION_REMEMBER_KEY))

    if not user_id or not secreto:
        flash('Primero inicia sesion para continuar.', 'warning')
        return redirect(url_for('auth.login'))

    form = OTPVerificationForm()

    if form.validate_on_submit():
        codigo = (form.codigo.data or '').strip()
        totp = pyotp.TOTP(secreto, interval=300)

        if not totp.verify(codigo, valid_window=1):
            flash('Codigo invalido o expirado. Intenta de nuevo.', 'danger')
            return render_template('auth/verificar_otp.html', form=form)

        user = Usuario.query.get(int(user_id))
        if not user or not user.estado:
            _limpiar_sesion_otp()
            flash('No se pudo completar la autenticacion.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        _limpiar_sesion_otp()

        flash(f'¡Bienvenido {user.username}!', 'success')
        return redirect_por_rol(user)

    return render_template('auth/verificar_otp.html', form=form)


@auth.route('/reenviar-otp', methods=['POST'])
def reenviar_otp():
    user_id = session.get(OTP_SESSION_USER_KEY)
    if not user_id:
        flash('Tu sesion de verificacion expiro. Inicia sesion de nuevo.', 'warning')
        return redirect(url_for('auth.login'))

    user = Usuario.query.get(int(user_id))
    if not user:
        _limpiar_sesion_otp()
        flash('No se encontro el usuario para reenviar codigo.', 'danger')
        return redirect(url_for('auth.login'))

    correo_destino = _obtener_correo_usuario(user)
    if not correo_destino:
        _limpiar_sesion_otp()
        flash('No se encontro un correo asociado para verificacion.', 'danger')
        return redirect(url_for('auth.login'))

    try:
        secreto = pyotp.random_base32()
        codigo = pyotp.TOTP(secreto, interval=300).now()
        _enviar_codigo_otp_por_correo(correo_destino, codigo, user.username)
        session[OTP_SESSION_SECRET_KEY] = secreto

        flash('Se envio un nuevo codigo de verificacion.', 'info')
    except Exception as e:
        current_app.logger.error(f"Error reenviando OTP por correo: {str(e)}")
        flash('No fue posible reenviar el codigo.', 'danger')

    return redirect(url_for('auth.verificar_otp'))

def redirect_por_rol(user):
    """Función auxiliar para redirigir según el rol del usuario"""
    if user.rol.nombre in ['Administrador']:
        return redirect(url_for('dashboard.index'))
    elif user.rol.nombre == 'Cajero':
        return redirect(url_for('pedidos.index'))
    elif user.rol.nombre == 'Cocinero':
        return redirect(url_for('produccion.index'))
    elif user.rol.nombre == 'Cliente':
        return redirect(url_for('tienda.menu'))
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
    _limpiar_sesion_otp()
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/redirigir')
@login_required
def redirigir():
    return redirect_por_rol(current_user)