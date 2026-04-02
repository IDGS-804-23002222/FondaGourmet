from flask import flash, redirect, url_for
from flask_login import login_user
from models import db, Usuario
from sqlalchemy import text
from werkzeug.security import generate_password_hash
from models import db, Usuario, Persona, Rol
import logging

logger = logging.getLogger(__name__)

def autenticar_usuario(username, password):
    user = Usuario.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        logger.warning(f"Intento de autenticación fallido para usuario: {username}")
        return None, "Credenciales inválidas"
    
    if user.estado != 'activo':
        logger.warning(f"Usuario inactivo: {username}")
        return None, "Tu cuenta está inactiva. Contacta al administrador."
    
    return user, None

def iniciar_sesion(user, remember=False):
    login_user(user, remember=remember)
    logger.info(f"Usuario autenticado: {user.username}")
    
def redireccionar_por_rol(user):
    rutas={
        1: 'dashboard.index',
        2: 'produccion.index',
        3: 'ventas.index',  
        4: 'tienda.index'
    }
    
    endpoint = rutas.get(user.id_rol, 'tienda.index')

    if endpoint:
        return redirect(url_for(endpoint))
    return redirect(url_for('auth.login'))